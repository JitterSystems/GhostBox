#!/bin/bash
echo "[*] Initializing GhostBox Environment for Parrot OS..."

sudo apt update
sudo apt install -y bwrap cage wayland-utils python3 xwayland libgl1-mesa-dri mesa-utils pciutils inxi

# Fix permissions for the virtualized layer
sudo usermod -aG video $USER
sudo usermod -aG render $USER

# Compile the Sentinel
gcc make_bpf.c -o make_bpf -lseccomp
./make_bpf

echo "[+] Dependencies installed and Sentinel active."
