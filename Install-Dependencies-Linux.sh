#!/bin/bash
# Linux dependency installer for Mesa Git History Viewer
set -e
sudo apt update
sudo apt install -y python3 python3-pip python3-tk git
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-dev.txt
