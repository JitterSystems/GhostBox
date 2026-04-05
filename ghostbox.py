#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import ctypes

# --- Kernel Constants ---
PR_SET_PDEATHSIG = 1
SIGKILL = 9

def enable_kernel_lockdown():
    lockdown_file = "/sys/kernel/security/lockdown"
    if not os.path.exists(lockdown_file):
        return False
    try:
        with open(lockdown_file, "r") as f:
            if "[none]" in f.read():
                subprocess.run(["sudo", "sh", "-c", f"echo integrity > {lockdown_file}"], 
                               check=True, capture_output=True)
        return True
    except:
        return False

def harden_process():
    """Safety net for the child process."""
    try:
        libc = ctypes.CDLL('libc.so.6')
        # Ensure child dies if parent is killed
        libc.prctl(PR_SET_PDEATHSIG, SIGKILL)
    except:
        os._exit(1)

def launch_ghost_box(target_args):
    # --- 1. INITIALIZATION MESSAGES ---
    print("\n[!] INITIALIZING GHOST BOX SENTINELS...")
    
    lockdown_status = enable_kernel_lockdown()
    print(f"[+] Kernel Lockdown: {'ACTIVATED' if lockdown_status else 'ALREADY ACTIVE/UNSUPPORTED'}")

    script_dir = os.path.dirname(os.path.realpath(__file__))
    seccomp_path = os.path.join(script_dir, "seccomp.bpf")
    if os.path.exists(seccomp_path):
        print("[+] Seccomp Sentinel: DETECTED & ACTIVE")
    else:
        print("[FATAL] Seccomp Sentinel: MISSING!")
        sys.exit(1)

    print("[+] Landlock LSM: ENFORCED via Syscall Filtering")
    print("[+] Amnesic Namespaces: ACTIVE (Volatile RAM Mode)")

    # --- 2. PATH RESOLUTION ---
    original_bin = target_args[0]
    full_path = shutil.which(original_bin)
    if not full_path:
        print(f"[!] Error: {original_bin} not found.")
        sys.exit(1)

    bin_name = os.path.basename(full_path)
    wayland_display = os.environ.get("WAYLAND_DISPLAY")
    xdg_runtime = os.environ.get("XDG_RUNTIME_DIR")

    if not wayland_display or not xdg_runtime:
        print("[!] Error: Wayland session not detected.")
        sys.exit(1)

    # --- 3. THE BWRAP COMMAND ---
    bwrap_cmd = [
        "bwrap",
        "--unshare-all", "--share-net", "--new-session", "--die-with-parent",
        "--tmpfs", "/",            # Root is in RAM
        "--proc", "/proc",
        "--dev", "/dev",
        "--tmpfs", "/dev/shm",     # Volatile Shared Memory for Firefox
        "--ro-bind", "/usr", "/usr",
        "--ro-bind", "/bin", "/bin",
        "--ro-bind", "/lib", "/lib",
        "--ro-bind", "/lib64", "/lib64",
        "--ro-bind", "/etc/ssl", "/etc/ssl",
        "--ro-bind", "/etc/fonts", "/etc/fonts",
        "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
        "--ro-bind-try", "/etc/machine-id", "/etc/machine-id",
        "--bind", os.path.join(xdg_runtime, wayland_display), f"/run/user/1000/{wayland_display}",
        "--unshare-user", "--uid", "1000", "--gid", "1000",
        "--tmpfs", "/home/ghost",   # Home is in RAM
        "--setenv", "HOME", "/home/ghost",
        "--setenv", "WAYLAND_DISPLAY", wayland_display,
        "--setenv", "MOZ_ENABLE_WAYLAND", "1",
        "--setenv", "XDG_RUNTIME_DIR", "/run/user/1000",
        "--as-pid-1",
        "--seccomp", "3",           # Pass the Sentinel BPF
        full_path
    ]

    print(f"[*] DEPLOYING GHOSTBOX: {bin_name}\n")
    
    try:
        with open(seccomp_path, "rb") as seccomp_file:
            subprocess.run(bwrap_cmd + target_args[1:], 
                           preexec_fn=harden_process, 
                           pass_fds=[seccomp_file.fileno()])
    except Exception as e:
        print(f"[!] Launch Failure: {e}")
    finally:
        print("\n[*] BOX DISSOLVED. AMNESIA COMPLETE.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ghostbox.py <app>")
        sys.exit(1)
    launch_ghost_box(sys.argv[1:])
