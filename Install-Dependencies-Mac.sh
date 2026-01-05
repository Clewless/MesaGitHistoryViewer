#!/bin/bash
# macOS dependency installer for Mesa Git History Viewer
set -e
echo "Installing dependencies..."
brew update
brew install python3 git
# Install tkinter (usually included with python3 from Homebrew)
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-dev.txt

echo ""
echo "Installation complete!"