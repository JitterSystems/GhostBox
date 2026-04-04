hostbox: The Obsidian Node Sandbox 🛡️🌑

Ghostbox is a high-security, amnesic application sandbox designed for Linux. It leverages Bubblewrap, Linux Namespaces, and a Binary Seccomp BPF filter to create a "digital vacuum" where applications are blind to your real OS, hardware, and identity.
🚀 Key Features
Feature	Protection Level	Technical Detail
Amnesic Filesystem	Extreme	Root (/) and Home are tmpfs (RAM). Everything is destroyed on exit.
Hardware Cloaking	High	Hides /sys. No motherboard serials, CPU info, or battery IDs.
Identity Spoofing	Total	Hostname is forced to obsidian-node and UID is mapped to 1000.
Active Seccomp	Hardened	A binary BPF filter kills the app if it attempts kernel-level exploits.
Wayland-Only	Safe	X11 is stripped out to prevent cross-window keylogging and spying.
GPU Shielding	Mitigation	Forces CPU rendering (llvmpipe) to bypass risky GPU drivers.
🛠️ Installation

Ensure you have the following dependencies on your host system:

    bubblewrap

    libseccomp-dev (for compiling the shield)

    gcc

1. Clone the Repository
Bash

git clone https://github.com/gothamblvck-coder/ghostbox.git
cd ghostbox

2. Generate the Binary Shield

To ensure the Seccomp filter matches your specific kernel architecture (e.g., x86_64), compile the BPF binary locally:
Bash

gcc make_bpf.c -o make_bpf -lseccomp && ./make_bpf

Note: You can delete the make_bpf executable after this step.

leave the make_bpf.c, ghostbox.py and the seccomp.bpf file only in the directory

🖥️ Usage

Run any application by passing its binary path to the script:
Bash

python3 ghostbox.py /usr/bin/firefox

📂 Repository Structure

    ghostbox.py: The main engine that handles namespaces and isolation logic.

    make_bpf.c: The C source code for the Seccomp filter (the "Blueprint").

    seccomp.bpf: The compiled binary filter used by the kernel (the "Shield").

    README.md: This file.

⚠️ Important Considerations

    No Persistence: Any files downloaded or settings changed inside the box are purged when the application closes.

    Network: This configuration uses --share-net. While your identity is hidden, your public IP remains visible unless you use a VPN on the host.

    Wayland Only: If your desktop environment uses X11, this sandbox will not launch. This is a deliberate security choice.
