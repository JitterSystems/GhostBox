🛡️ Ghostbox: The Obsidian Node Sandbox 🌑

Ghostbox is an ultra-hardened, amnesic application sandbox for Linux. It goes beyond traditional containerization by implementing a 5-Wall Defense System, combining Linux Namespaces, Kernel Lockdown, and a custom Go-based Sentry Kernel that intercepts and spoofs system calls in real-time.

It creates a "digital vacuum" where applications are blind to your real OS, hardware, and identity.
🚀 The 5-Wall Defense
Wall	Component	Protection Level	Technical Detail
1	Amnesic FS	Extreme	Root (/) and Home are tmpfs (RAM). Data vanishes on exit.
2	Hardware Cloak	High	Hides /sys. Masks CPU, Motherboard, and Battery IDs.
3	Active Seccomp	Hardened	Binary BPF filter kills the app if it touches risky Kernel functions.
4	Kernel Lockdown	Total	Forces Integrity Lockdown to prevent Root-level memory modifications.
5	The Sentry (Go)	Unbreakable	NEW: A syscall interposer that "lies" to the app and blocks forensics.
🛠️ Requirements & Dependencies

You must install these dependencies on your host system to build the Sentry and the Shield:
Bash

sudo apt update
sudo apt install bubblewrap libseccomp-dev gcc golang-go python3

📥 Installation & Setup
1. Clone the Repository
Bash

git clone https://github.com/gothamblvck-coder/ghostbox.git
cd ghostbox

2. Generate the Binary Shield (Wall 3)

Compile the Seccomp BPF filter to match your specific kernel architecture:
Bash

gcc make_bpf.c -o make_bpf -lseccomp && ./make_bpf

3. Build the Sentry Kernel (Wall 5)

Compile the Go-based syscall interposer that monitors the sandbox from the outside:
Bash

go build -o sentry sentry.go

Note: Ensure the sentry binary remains in the same directory as ghostbox.py.
🖥️ Usage

Pass any application binary path to the Ghostbox engine. The script will automatically trigger the Kernel Lockdown, load the Seccomp Shield, and boot the Sentry Interposer.
Bash

# Example: Run a browser (Wayland only)
python3 ghostbox.py /usr/bin/firefox

# Example: Run a terminal tool
python3 ghostbox.py /usr/bin/curl -- https://checkip.amazonaws.com

📂 Repository Structure

ghostbox.py: The Orchestrator. Manages namespaces, mounts, and lockdown logic.

sentry.go: The 5th Wall source. A ptrace-based Go supervisor for syscall spoofing.

sentry: The compiled Sentry binary (The Interposer).

make_bpf.c: The C blueprint for the Seccomp filter.

seccomp.bpf: The compiled binary "Shield" used by the kernel.

⚠️ Anti-Forensic Policies

Unlike standard sandboxes, Ghostbox employs Active Deception:

Identity Spoofing: uname and sysinfo calls are intercepted to return generic/fake system data.

Inbound Block: Prevents the application from listening for incoming connections, stopping reverse shells.

Nested Block: Prevents the app from using unshare to hide from the Sentry.

Wayland Only: X11 is strictly forbidden to prevent cross-window keylogging.

🛑 Important Considerations

No Persistence: Any files downloaded or settings changed are purged instantly when the box dissolves.

Network: Uses --share-net. Your identity is hidden, but your IP is visible. Use a VPN on the host for total anonymity.

Sudo Requirement: ghostbox.py requires a brief sudo prompt at launch to enable Kernel Lockdown. Once locked, the app runs with zero privileges.
