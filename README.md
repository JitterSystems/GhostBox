Big Thanks to Jesus for making this gain attention! Turn to Jesus before it's too late. :) He loves You

🛡️ Ghostbox: The Obsidian Node Sandbox 🌑

Beta Mode

Ghostbox is an ultra-hardened, amnesic application sandbox for Linux. It creates a "digital vacuum" where applications are blind to your real OS, hardware, and identity. By utilizing a 4-Wall Defense System, it ensures that any application running inside has zero persistence and zero visibility into the host system.
🚀 The 4-Wall Defense
Wall	Component	Protection Level	Technical Detail

1.	Amnesic FS	Extreme	Root (/) and Home are tmpfs (RAM). Data vanishes on exit.

2.	Binary Sentinel	Hardened	Binary BPF filter kills the app if it touches risky Kernel functions.

3.	BPF Landlock >> Prevents anything outside the ghostbox/sandbox from being touched

4.	Hardware Cloak	High	Hides /sys. Masks GPU, Motherboard, PCI etc.

🛠️ Requirements & Dependencies

You must install these dependencies on your host system to build the Shield and run the Orchestrator:
Bash

sudo apt update
sudo apt install bubblewrap libseccomp-dev gcc python3


install the dependencies:

chmod +x setup.sh && bash setup.sh


📥 Installation & Setup
1. Clone the Repository
Bash

git clone https://github.com/gothamblvck-coder/ghostbox.git
cd ghostbox

2. Generate the Binary Shield (Wall 3)

Compile the Seccomp BPF filter to match your specific kernel architecture. This creates the seccomp.bpf file that the Python script loads into the kernel.
Bash

gcc make_bpf.c -o make_bpf -lseccomp && ./make_bpf

🖥️ Usage

Pass any application binary path to the Ghostbox engine. The script will automatically trigger the Kernel Lockdown, load the Seccomp Shield, and spawn the amnesic environment.
Bash

# Example: Run a browser (Wayland only)
python3 ghostbox.py /usr/bin/firefox

# Example: Run a terminal tool
python3 ghostbox.py /usr/bin/curl -- https://checkip.amazonaws.com

📂 Repository Structure

ghostbox.py: The Orchestrator. Manages namespaces, RAM mounts, and kernel lockdown logic.

make_bpf.c: The C blueprint for the Seccomp filter.

seccomp.bpf: The compiled binary "Shield" used by the kernel to block dangerous syscalls.

⚠️ Security Policies

Zero Persistence: Any files downloaded or settings changed are purged instantly when the box dissolves.

Hardware Anonymization: The app sees a generic "obsidian-node" hostname and a masked /sys directory.

Wayland Only: X11 is strictly discouraged/blocked where possible to prevent cross-window keylogging and screen scraping.

Privilege Death: Uses NO_NEW_PRIVS to ensure that even if an app finds a vulnerability, it can never escalate to Root.

🛑 Important Considerations

Network: Uses --share-net. Your identity is hidden, but your IP is visible to the destination. Use ShadowNet on the host to achieve even more anonymity

Sudo Requirement: ghostbox.py requires a brief sudo prompt at launch to enable Kernel Lockdown. Once the kernel is locked and the sandbox is built, the application runs as a standard, unprivileged user.

Amnesia: If you need to save a file, you must move it out of the sandbox before closing the app, or it will be lost forever.
