#!/bin/bash
# macOS launcher for Mesa Git History Viewer

# Check if Python3 is available
if ! command -v python3 &> /dev/null
then
    echo "Error: python3 is not installed or not in PATH."
    echo "Please install Python3 (e.g., via Homebrew: brew install python3)"
    exit 1
fi

# Check if tkinter is available
if ! python3 -c "import tkinter" &> /dev/null
then
    echo "Error: tkinter is not available in your Python installation."
    echo "Please install Python with tkinter support (e.g., via Homebrew: brew install python3)"
    exit 1
fi

# Check if mesa_viewer.py exists
if [ ! -f "mesa_viewer.py" ]; then
    echo "Error: mesa_viewer.py not found in the current directory."
    exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null
then
    echo "Warning: git is not installed or not in PATH."
    echo "The application will run but git-dependent features will be disabled."
fi

echo "Starting Mesa Git History Viewer..."
python3 mesa_viewer.py
