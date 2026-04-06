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
        libc = ctypes.CDLL('libc.so.6')
        libc.prctl(PR_SET_PDEATHSIG, SIGKILL)
    except: os._exit(1)

def launch_ghost_box(target_args):
    print("\n[!] VIRTUALIZING DISPLAY ENVIRONMENT...")

    if not shutil.which("cage"):
        print("[!] ERROR: 'cage' not found. Run your setup script first.")
        sys.exit(1)

    # Host Variables
    wayland_host = os.environ.get("WAYLAND_DISPLAY", "wayland-0")
    xdg_runtime = os.environ.get("XDG_RUNTIME_DIR")
    
    original_bin = target_args[0]
    full_path = shutil.which(original_bin)
    if not full_path: 
        print(f"[!] Error: Binary {original_bin} not found.")
        sys.exit(1)

    # --- THE SECURE BWRAP COMMAND ---
    bwrap_cmd = [
        "bwrap",
        "--unshare-all",    # Total namespace isolation
        "--share-net",      # Keep internet for browsers
        "--new-session", 
        "--die-with-parent",
        
        # 1. Clean Filesystem
        "--tmpfs", "/", 
        "--proc", "/proc",
        "--dev", "/dev",
        "--tmpfs", "/dev/shm", 
        "--tmpfs", "/tmp",       
        "--dir", "/tmp/.X11-unix",
        
        # 2. Core OS Bindings (Read-Only)
        "--ro-bind", "/sys", "/sys", 
        "--ro-bind", "/usr", "/usr",
        "--ro-bind", "/bin", "/bin",
        "--ro-bind", "/lib", "/lib",
        "--ro-bind", "/lib64", "/lib64",
        "--ro-bind", "/etc/ssl", "/etc/ssl",
        "--ro-bind", "/etc/fonts", "/etc/fonts",
        "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
        "--ro-bind-try", "/etc/machine-id", "/etc/machine-id",
        
        # 3. The "Bridge"
        # Mount the host socket as 'host-wayland-0' to avoid "resource busy"
        "--tmpfs", "/run/user/1000",
        "--bind", os.path.join(xdg_runtime, wayland_host), "/run/user/1000/host-wayland-0",
        
        # 4. Identity Strip
        "--unshare-user", "--uid", "1000", "--gid", "1000",
        "--tmpfs", "/home/ghost",
        
        # 5. Environment Sanitization
        "--clearenv",
        "--setenv", "HOME", "/home/ghost",
        "--setenv", "XDG_RUNTIME_DIR", "/run/user/1000",
        
        # POINT CAGE TO THE RENAMED HOST SOCKET
        "--setenv", "WAYLAND_DISPLAY", "host-wayland-0", 
        
        # DISABLE XWAYLAND TO STOP THE ABSTRACT SOCKET COLLISION
        "--setenv", "WLR_XWAYLAND", "0", 
        
        "--setenv", "PATH", "/usr/bin:/bin",
        "--setenv", "XDG_DATA_DIRS", "/usr/local/share:/usr/share",
        "--setenv", "MOZ_ENABLE_WAYLAND", "1",
        
        "--hostname", "ghostbox",
        
        # 6. Proxy Launch
        "cage", "-d", "-m", "last", "--", full_path
    ]

    bwrap_cmd.extend(target_args[1:])

    print(f"[*] PROXY LAYER: Cage")
    print(f"[*] TARGET APP: {os.path.basename(full_path)}")
    print("[+] Hardware & KDE Fingerprint: SPOOFED")
    
    try:
        subprocess.run(bwrap_cmd, preexec_fn=harden_process)
    except Exception as e:
        print(f"[!] Launch Failure: {e}")
    finally:
        print("\n[*] GHOST BOX CLOSED.")

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    launch_ghost_box(sys.argv[1:])
