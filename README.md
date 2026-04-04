Obsidian-Node: The GhostBox
"What the Sovereigns haven't seen, they cannot track."

Obsidian-Node (GhostBox) is a high-security, unprivileged, and amnesic sandboxing tool for Linux. Built on the bubblewrap (bwrap) engine, it is designed for users who require total digital sovereignty, anti-forensic persistence, and hardware-level anonymity.

While traditional tools like Flatpak focus on convenience, Obsidian-Node focuses on The Void: ensuring that every application runs in a temporary, cloaked environment that evaporates instantly upon closing.
🛠 Key Features

    Amnesic Filesystem: Uses --tmpfs for / and /home. Every file, cookie, and log created during the session exists only in RAM and is wiped on exit.

    Hardware Cloaking: Masks your motherboard serials, PCI bus, and firmware by black-holing /sys.

    GPU Stealth: Forces LLVMpipe software rendering via LIBGL_ALWAYS_SOFTWARE=1, preventing hardware-based browser fingerprinting.

    Zero-Privilege Architecture: Unlike Firejail, it does not use SUID binaries. It leverages unprivileged user namespaces, meaning the sandbox itself has no path to root.

    Kernel Hardening: Employs PR_SET_NO_NEW_PRIVS to ensure sandboxed processes can never escalate privileges, even if a vulnerability is found.

    Network Sanitization: Restricts the environment to minimalist /etc/ maps to prevent local network discovery and DNS leaking.

⚖️ The "Ghost" Comparison

Why Obsidian-Node is the superior choice for absolute privacy:
Feature	Obsidian-Node	Firejail	AppArmor	SELinux
Philosophy	Total Amnesia	Ease of Use	Path Restriction	Label Enforcement
Privilege	🏆 Unprivileged	❌ SUID Root	Kernel-Level	Kernel-Level
Hardware Hiding	🏆 Full Masking	Partial	None	None
Forensic Trace	🏆 Zero	Persistent Cache	Persistent	Persistent
Attack Surface	Minimal (bwrap)	❌ High (CVE prone)	Low	High Complexity
Why it beats the "Industry Standards":

    Vs. Firejail: Firejail is an SUID-root binary. If a hacker finds a bug in Firejail, they get root access to your host. Obsidian-Node uses bwrap, which is audited, minimalist, and runs entirely in user-space.

    Vs. AppArmor: AppArmor is a passive "wall." It stops an app from touching a folder, but it doesn't hide your identity. It won't stop an app from seeing your real GPU or your motherboard ID.

    Vs. SELinux: SELinux is incredibly complex and often "noisy." Obsidian-Node is "Default-Deny"—if you didn't explicitly map a resource in the script, it simply does not exist to the application.

🚀 Installation

    Install Bubblewrap:
    Bash

sudo apt install bubblewrap  # Debian/Ubuntu
sudo pacman -S bubblewrap    # Arch

Deploy GhostBox:
Move your ghostbox.py to /usr/local/bin/ghostbox and make it executable:
Bash

sudo chmod +x /usr/local/bin/ghostbox
sudo chown root:root /usr/local/bin/ghostbox

Usage:
Bash

    ghostbox firefox
    # or
    ghostbox bash  # Enter a fully sandboxed shell

🛡 Security Mandate

Obsidian-Node is designed for Wayland environments. If you are using X11, be aware that the X11 protocol allows any window to log the keystrokes of another. For true isolation, use a Wayland compositor (GNOME, KDE Plasma 6, Sway).

The Sovereigns are watching. Give them nothing to see.
