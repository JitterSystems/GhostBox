#!/bin/bash
# GhostBox Deployment Script

echo "[*] Initializing GhostBox Environment for Parrot OS..."

# 1. Install necessary binaries
sudo apt update
sudo apt install -y bwrap cage wayland-utils python3 xwayland libgl1-mesa-dri

# 2. Ensure the user has the right permissions for DRI (Direct Rendering)
sudo usermod -aG video $USER
sudo usermod -aG render $USER

echo "[+] Dependencies installed. Please restart your terminal if this is the first time."
