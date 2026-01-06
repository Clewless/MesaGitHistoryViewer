#!/bin/bash
# macOS dependency installer for Mesa Git History Viewer
set -e

# Check for Homebrew
if ! command -v brew &> /dev/null
then
    echo "Homebrew not found. Please install Homebrew to continue."
    echo "See https://brew.sh/ for installation instructions."
    exit 1
fi

echo "Installing dependencies..."
brew update

# Install git (if not already installed via Xcode Command Line Tools)
if ! command -v git &> /dev/null
then
    echo "Installing git..."
    brew install git
else
    echo "Git is already installed: $(git --version)"
fi

# Install Python3 (tkinter should be included)
echo "Installing Python3..."
brew install python3

# Upgrade pip
python3 -m pip install --upgrade pip

# Install development dependencies (these are only needed for development)
if [ -f "requirements-dev.txt" ]; then
    echo "Installing development dependencies..."
    python3 -m pip install -r requirements-dev.txt
else
    echo "Warning: requirements-dev.txt not found. This is only needed for development."
fi

echo "Verifying tkinter installation..."
if ! python3 -c "import tkinter; root = tkinter.Tk(); root.withdraw(); root.destroy()" &> /dev/null
then
    echo "tkinter not found or not working properly. This is sometimes an issue with how Python is installed."
    echo "Please try reinstalling Python with Homebrew: brew reinstall python3"
    exit 1
fi

echo ""
echo "Installation complete!"
echo "You can now run the application using: ./Run-Viewer-Mac.sh"