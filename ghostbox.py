#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import ctypes

# --- Kernel Enforcement Constants ---
PR_SET_NO_NEW_PRIVS = 38
PR_SET_PDEATHSIG = 1
SIGKILL = 9

def enable_kernel_lockdown():
    """ 
    Automatically ensures the Kernel is in Lockdown Mode.
    This prevents even a 'Root' user from modifying the running kernel memory.
    """
    lockdown_file = "/sys/kernel/security/lockdown"
    if not os.path.exists(lockdown_file):
        print("[!] Kernel Lockdown not supported by this kernel.")
        return

    with open(lockdown_file, "r") as f:
        current_state = f.read()

    # If [none] is highlighted, it means Lockdown is NOT active.
    if "[none]" in current_state:
        print("[*] Shielding Kernel: Enabling Integrity Lockdown...")
        try:
            # Briefly use sudo to bolt the door, then it's never used again.
            subprocess.run([
                "sudo", "sh", "-c", f"echo integrity > {lockdown_file}"
            ], check=True)
            print("[+] Kernel Locked: Integrity Mode Active.")
        except subprocess.CalledProcessError:
            print("[!] Failed to lock kernel. Proceeding with standard isolation.")
    else:
        print("[*] Kernel Security: Lockdown already active.")

def harden_process():
    """ 
    The Unclimbable Wall: Runs INSIDE the sandbox before the app executes. 
    This ensures the 'Rootless' and 'Privilege-Locked' state.
    """
    libc = ctypes.CDLL('libc.so.6')
    
    # 1. NO_NEW_PRIVS: The ultimate SetUID blocker.
    # It is physically impossible for the process to ever gain more power.
    libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)
    
    # 2. PDEATHSIG: Ensure the app dies if the parent script is terminated.
    libc.prctl(PR_SET_PDEATHSIG, SIGKILL)

def launch_ghost_box(target_args):
    # STEP 1: Bolting the Kernel Door
    enable_kernel_lockdown()

    original_bin = target_args[0]
    full_path = shutil.which(original_bin) or os.path.abspath(original_bin)
    
    if not os.path.exists(full_path):
        print(f"[!] Error: {original_bin} not found.")
        return

    app_dir = os.path.dirname(full_path)
    bin_name = os.path.basename(full_path)
    
    # Locate seccomp.bpf in the same directory as this script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    seccomp_path = os.path.join(script_dir, "seccomp.bpf")

    # STEP 2: Building the Bubble (Bubblewrap command)
    bwrap_cmd = [
        "bwrap",
        "--unshare-all",        # Separate PID, IPC, UTS, Mount, User, Cgroup
        "--share-net",          # Shared network (use a VPN on the host!)
        "--new-session",
        "--die-with-parent",
        
        # --- THE MIRAGE (Namespaces) ---
        "--tmpfs", "/",         # Root is RAM (Amnesia)
        "--proc", "/proc",
        "--dev", "/dev",
        "--tmpfs", "/sys",      # BLACKOUT: Hides hardware serials
        
        # --- THE READ-ONLY SYSTEM CORE ---
        "--ro-bind", "/usr", "/usr",
        "--ro-bind", "/bin", "/bin",
        "--ro-bind", "/lib", "/lib",
        "--ro-bind", "/lib64", "/lib64",
        "--ro-bind", "/etc/ssl", "/etc/ssl",
        "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
        
        # --- THE IDENTITY SPOOF ---
        "--hostname", "obsidian-node",
        "--unshare-user",
        "--uid", "1000",
        "--gid", "1000",
        "--tmpfs", "/home/ghost",
        "--dir", "/run/user/1000",
        
        # --- THE HARDWARE CLOAK ---
        "--setenv", "LIBGL_ALWAYS_SOFTWARE", "1", # Bypass GPU driver exploits
        "--setenv", "GALLIUM_DRIVER", "llvmpipe",
        
        "--ro-bind", app_dir, "/app",
        "--clearenv",
        "--setenv", "HOME", "/home/ghost",
        "--setenv", "PATH", "/usr/bin:/bin:/app",
        "--setenv", "XDG_RUNTIME_DIR", "/run/user/1000",
        "--as-pid-1",
    ]

    # STEP 3: Loading the Sentinel (Seccomp)
    seccomp_file = None
    if os.path.exists(seccomp_path):
        print(f"[*] Loading Seccomp Sentinel: {seccomp_path}")
        # Open the BPF file; we will pass its file descriptor to bwrap
        seccomp_file = open(seccomp_path, "rb")
        # File descriptor '3' is usually the first available after stdin/out/err
        bwrap_cmd += ["--seccomp", "3"]
    else:
        print("[!] Warning: seccomp.bpf not found. Sentinel is INACTIVE.")

    # STEP 4: Wayland-Only Protection
    xdg_runtime = os.environ.get("XDG_RUNTIME_DIR")
    wayland_display = os.environ.get("WAYLAND_DISPLAY")
    if xdg_runtime and wayland_display:
        wayland_path = os.path.join(xdg_runtime, wayland_display)
        if os.path.exists(wayland_path):
            bwrap_cmd += ["--bind", wayland_path, f"/run/user/1000/{wayland_display}"]
            bwrap_cmd += ["--setenv", "WAYLAND_DISPLAY", wayland_display]

    final_bin = os.path.join("/app", bin_name)
    full_command = bwrap_cmd + [final_bin] + target_args[1:]

    print(f"[*] DEPLOYING GHOSTBOX: {bin_name}")
    try:
        # STEP 5: DROP PRIVILEGES & LAUNCH
        # pass_fds=[3] ensures the bwrap process can access the seccomp file descriptor
        subprocess.run(
            full_command, 
            preexec_fn=harden_process, 
            pass_fds=[3] if seccomp_file else []
        )
    finally:
        if seccomp_file: 
            seccomp_file.close()
        print("[*] BOX DISSOLVED. AMNESIA COMPLETE.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 ghostbox.py <app_name_or_path>")
        sys.exit(1)
    launch_ghost_box(sys.argv[1:])
