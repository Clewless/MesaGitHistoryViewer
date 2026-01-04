@echo off
REM Windows dependency installer for Mesa Git History Viewer
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
REM If tkinter is missing, install via python -m pip install tk (for some Python distributions)
