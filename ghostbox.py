#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import ctypes

# --- Kernel Safety ---
PR_SET_PDEATHSIG = 1
SIGKILL = 9

def harden_process():
    try:
        # Ensures if the Python launcher dies, the sandbox is killed by the kernel
        libc = ctypes.CDLL('libc.so.6')
        libc.prctl(PR_SET_PDEATHSIG, SIGKILL)
    except: os._exit(1)

def launch_ghost_box(target_args):
    print("\n[!] VIRTUALIZING DISPLAY ENVIRONMENT...")

    bpf_path = os.path.abspath("seccomp.bpf")
    if not os.path.exists(bpf_path):
        print("[!] FATAL: 'seccomp.bpf' not found!")
        sys.exit(1)

    if not shutil.which("cage"):
        print("[!] ERROR: 'cage' not found.")
        sys.exit(1)

    wayland_host = os.environ.get("WAYLAND_DISPLAY", "wayland-0")
    xdg_runtime = os.environ.get("XDG_RUNTIME_DIR")
    
    # Path Detection for Browsers
    original_bin = target_args[0]
    full_path = shutil.which(original_bin)
    if not full_path: 
        print(f"[!] Error: Binary {original_bin} not found.")
        sys.exit(1)
    
    bin_dir = os.path.dirname(os.path.realpath(full_path))

    # The Pipe Bridge for BPF Data
    r, w = os.pipe()
    os.set_inheritable(r, True)
    with open(bpf_path, "rb") as f:
        bpf_data = f.read()

    bwrap_cmd = [
        "bwrap",
        "--unshare-all",     # Isolate Network, PID, IPC, UTS, and User namespaces
        "--share-net",       # Allow network access
        "--new-session",     # Disconnect from terminal session
        "--die-with-parent", 
        
        "--seccomp", str(r), # Load the BPF Sentinel via Pipe
        
        # 1. AMNESIC ROOT (Everything is in RAM)
        "--tmpfs", "/", 
        "--proc", "/proc",
        "--dev", "/dev",
        "--tmpfs", "/dev/shm", 
        "--tmpfs", "/tmp",       
        "--dir", "/tmp/.X11-unix",
        
        # 2. HARDWARE & BUS CLOAKING (The Anti-Fingerprint Layer)
        "--tmpfs", "/sys",
        "--dir", "/sys/bus/pci/devices", # Wipes PCI bus info
        "--dir", "/sys/bus/usb/devices", # Wipes USB bus info
        "--dir", "/sys/class/dmi",       # Wipes BIOS/Serial info
        "--dir", "/sys/firmware",        # Wipes UEFI info
        "--ro-bind-try", "/sys/dev", "/sys/dev",
        "--ro-bind-try", "/sys/devices/system/cpu", "/sys/devices/system/cpu",
        
        # 3. CORE OS & APP BINDINGS (Read-Only)
        "--ro-bind", "/usr", "/usr",
        "--ro-bind", "/bin", "/bin",
        "--ro-bind", "/lib", "/lib",
        "--ro-bind", "/lib64", "/lib64",
        "--ro-bind", "/etc/ssl", "/etc/ssl",
        "--ro-bind", "/etc/fonts", "/etc/fonts",
        "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
        "--ro-bind-try", bin_dir, bin_dir, 
        "--tmpfs", "/etc/machine-id",    # Volatile Machine ID
        
        # 4. WAYLAND BRIDGE (Display Isolation)
        "--tmpfs", "/run/user/1000",
        "--bind", os.path.join(xdg_runtime, wayland_host), "/run/user/1000/host-wayland-0",
        
        # 5. IDENTITY STRIP
        "--unshare-user", "--uid", "1000", "--gid", "1000",
        "--tmpfs", "/home/ghost",        # Disposable Home directory
        "--tmpfs", "/run/dbus",          # Sever D-Bus fingerprinting
        
        # 6. ENVIRONMENT SANITIZATION
        "--clearenv",
        "--setenv", "HOME", "/home/ghost",
        "--setenv", "XDG_RUNTIME_DIR", "/run/user/1000",
        "--setenv", "WAYLAND_DISPLAY", "host-wayland-0", 
        "--setenv", "WLR_XWAYLAND", "0", 
        "--setenv", "PATH", "/usr/bin:/bin:" + bin_dir,
        "--setenv", "MOZ_ENABLE_WAYLAND", "1",
        
        # GPU SPOOFING
        "--setenv", "WLR_RENDERER", "pixman",
        "--setenv", "LIBGL_ALWAYS_SOFTWARE", "1",
        "--setenv", "GALLIUM_DRIVER", "llvmpipe",
        
        "--hostname", "ghostbox",
        "cage", "-d", "-m", "last", "--", full_path
    ]

    bwrap_cmd.extend(target_args[1:])

    os.write(w, bpf_data)
    os.close(w)

    try:
        subprocess.run(bwrap_cmd, pass_fds=(r,), preexec_fn=harden_process)
    except Exception as e:
        print(f"[!] Launch Failure: {e}")
    finally:
        os.close(r)
        print("\n[*] GHOST BOX CLOSED.")

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    launch_ghost_box(sys.argv[1:])
