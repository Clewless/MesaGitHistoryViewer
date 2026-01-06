#!/bin/bash
# Linux dependency installer for Mesa Git History Viewer
set -e

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect OS distribution. /etc/os-release not found."
    exit 1
fi

echo "Detected Linux distribution: $OS"

if [[ "$OS" == "ubuntu" || "$OS" == "debian" || "$OS" == "linuxmint" || "$OS" == "pop" ]]; then
    echo "Installing dependencies for Debian/Ubuntu..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-tk git
elif [[ "$OS" == "fedora" ]]; then
    echo "Installing dependencies for Fedora..."
    sudo dnf install -y python3 python3-pip python3-tkinter git
elif [[ "$OS" == "arch" || "$OS" == "manjaro" ]]; then
    echo "Installing dependencies for Arch Linux..."
    sudo pacman -Syu --noconfirm python python-pip tk git
else
    echo "Unsupported distribution: $OS"
    echo "Please manually install the following packages: python3, python3-pip, python3-tk, and git."
    echo "After installing the dependencies, run the following command:"
    echo "python3 -m pip install -r requirements-dev.txt"
    exit 1
fi

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-dev.txt

echo "Installation complete!"