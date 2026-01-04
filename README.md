```
███╗   ███╗███████╗███████╗ █████╗ 
████╗ ████║██╔════╝██╔════╝██╔══██╗
██╔████╔██║█████╗  ███████╗███████║
██║╚██╔╝██║██╔══╝  ╚════██║██╔══██║
██║ ╚═╝ ██║███████╗███████║██║  ██║
╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝
                                   
██████╗ ██╗████████╗
██╔════╝ ██║╚══██╔══╝
██║  ███╗██║   ██║   
██║   ██║██║   ██║   
╚██████╔╝██║   ██║   
 ╚═════╝ ╚═╝   ╚═╝   

██╗  ██╗██╗███████╗████████╗ ██████╗ ██████╗ ██╗   ██╗
██║  ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝
███████║██║███████╗   ██║   ██║   ██║██████╔╝ ╚████╔╝ 
██╔══██║██║╚════██║   ██║   ██║   ██║██╔══██╗  ╚██╔╝  
██║  ██║██║███████║   ██║   ╚██████╔╝██║  ██║   ██║   
╚═╝  ╚═╝╚═╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   

██╗   ██╗██╗███████╗██╗    ██╗███████╗██████╗ 
██║   ██║██║██╔════╝██║    ██║██╔════╝██╔══██╗
██║   ██║██║█████╗  ██║ █╗ ██║█████╗  ██████╔╝
╚██╗ ██╔╝██║██╔══╝  ██║███╗██║██╔══╝  ██╔══██╗
 ╚████╔╝ ██║███████╗╚███╔███╔╝███████╗██║  ██║
  ╚═══╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝
```

A desktop application for browsing Mesa's Git history with a local searchable database and release notes viewer.

## Why?

Mesa implements changes quickly over many releases. For developers who haven't kept up with development, it's time-consuming to search through every release's changelog. This tool lets you **Ctrl+F through the entire change history** within a timeframe to find specific changes instantly.

Also includes a tool to dump the last X months of logs into a clean list—handy for exporting to other tools or parsing in your text editor.

## Features

### Deep Dive (History)
Local, searchable table of the last 12 months of commits. Type keywords, commit hashes, or file changes to instantly filter results.

### Summaries (Release Notes)
Parses the `.rst` files from the Mesa docs folder so you can read release notes side-by-side with the history.

### Aggregated List Export
Grab the last X months of history and dump it into a text box. One-click copy to paste into other tools.

## Screenshots

### Deep Dive (History)
![History tab showing searchable commit table](screenshots/history-tab.png)

### Summaries (Release Notes)
![Summaries tab with release notes viewer](screenshots/summaries-tab.png)

### Aggregated List Export
![Export tab for exporting commit history](screenshots/export-tab.png)

## Requirements

- **Python 3.9** or higher
- **Git** (in your PATH)
- **tkinter** (usually included with Python)
- **Supported on**: Windows, macOS, and Linux (Fedora, Arch, Ubuntu, Debian)

## Installation & Setup

### Step 1: Install Dependencies

Choose the script for your OS:

- **Windows**: Double-click `Install-Dependencies-Windows.bat`
- **Linux**: Run `bash Install-Dependencies-Linux.sh`
- **macOS**: Run `bash Install-Dependencies-Mac.sh`

### Step 2: Run the Viewer

Choose the script for your OS:

- **Windows**: Double-click `Run-Viewer-Windows.bat`
- **Linux**: Run `bash Run-Viewer-Linux.sh`
- **macOS**: Run `bash Run-Viewer-Mac.sh`

**First time?** Click "Download/Update Mesa Repo" to fetch the Mesa source code (may take a few minutes on first run).

> **Note**: Launcher scripts can be run from any working directory; the application uses its own code location to find cache and repo files.

## Troubleshooting: Tcl/Tk and tkinter

If the app fails to start with an error about Tcl/Tk or "Can't find a usable init.tcl", follow these steps:

```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk

# macOS
brew install python
# or ensure your Python distribution includes Tk support;
# ActiveTcl may be required in some setups

# Windows
# Reinstall Python from python.org and ensure
# "Tcl/Tk and IDLE" is selected during installation
```

If you see a warning about Python version, install **Python 3.9+** to match the recommended testing configuration.

## Diagnostics & Quick Health Check

Run a diagnostic report to check Python, Tcl/Tk, Git, and project layout without starting the GUI:

```bash
python mesa_viewer.py --diagnose
```

This will print a summary and exit with a non-zero code if a fatal issue is detected.

You can also run an interactive helper to attempt remedial actions (like installing tkinter via your package manager):

```bash
python mesa_viewer.py --fix
```

Or combine both:

```bash
python mesa_viewer.py --diagnose --fix
```

## Usage

- **Filter commits**: Type keywords, file names, or hashes in the search bar (e.g., "radv", "fix", commit hash)
- **View release notes**: Click a version on the left pane to see what changed in that release
- **Export logs**: Go to "Aggregated List Export", set a month range, generate, and copy to clipboard

## Files

| File | Purpose |
|------|---------|
| `mesa_viewer.py` | Main application |
| `Mesa_Deep_Dive.txt` | Generated git log cache (git history) |
| `Mesa_Summaries.txt` | Generated release notes cache |
| `mesa/` | Mesa Git repository (auto-downloaded on first use) |

## License

Open source. Use it however you want.

## Notes

This project was vibe coded with human oversight.
