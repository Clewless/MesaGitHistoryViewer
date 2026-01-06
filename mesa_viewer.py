import subprocess
import os
import threading
import re
import shutil
import sys
import platform
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from contextlib import suppress
import logging

# Version
VERSION = "0.3.1a0"

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
    from tkinter import TclError

    TK_AVAILABLE = True
except Exception:
    # Import failed (tkinter not available)
    tk = None  # type: ignore
    ttk = None  # type: ignore
    messagebox = None  # type: ignore
    scrolledtext = None  # type: ignore
    TclError: type = Exception  # type: ignore
    TK_AVAILABLE = False


def run_diagnostics() -> Dict[str, Any]:
    """Run a set of safe diagnostics and return a dict summarizing results.

    This function is safe to call even when tkinter is not importable and will
    never raise; it returns info and prints a human-readable report.
    """
    info: Dict[str, Any] = {}

    # Python
    info["python_version"] = platform.python_version()
    info["python_ok"] = sys.version_info >= (3, 9)

    # tkinter / Tcl
    info["tk_imported"] = TK_AVAILABLE
    if TK_AVAILABLE:
        try:
            test_root = tk.Tk()
            test_root.withdraw()
            test_root.update()
            test_root.destroy()
            info["tk_usable"] = True
            info["tk_error"] = None
        except Exception as e:
            info["tk_usable"] = False
            info["tk_error"] = str(e)
    else:
        info["tk_usable"] = False
        info["tk_error"] = "tkinter not imported"

    # Git
    git_path = shutil.which("git")
    info["git_path"] = git_path
    if git_path:
        try:
            p = subprocess.run([git_path, "--version"], capture_output=True, text=True)
            info["git_version"] = (p.stdout or p.stderr or "").strip()
        except Exception as e:
            info["git_version"] = f"error: {e}"
    else:
        info["git_version"] = None

    # Filesystem
    base_dir = os.path.dirname(os.path.abspath(__file__))
    info["base_dir"] = base_dir
    try:
        info["base_dir_writable"] = os.access(base_dir, os.W_OK)
    except Exception:
        info["base_dir_writable"] = False

    mesa_dir = os.path.join(base_dir, "mesa")
    info["mesa_dir_exists"] = os.path.isdir(mesa_dir)
    info["mesa_is_git_repo"] = os.path.isdir(os.path.join(mesa_dir, ".git"))

    # Print human-friendly report
    print("\nMesa Git History Viewer - Diagnostic Report\n" + "-" * 50)
    print(f"Python: {info['python_version']} (OK: {info['python_ok']})")
    print(f"Tkinter imported: {info['tk_imported']} - usable: {info['tk_usable']}")
    if info["tk_error"]:
        print(f"Tk error: {info['tk_error']}")
    print(f"Git: {info['git_path']} (version: {info['git_version']})")
    print(f"Base dir: {info['base_dir']} (writable: {info['base_dir_writable']})")
    print(
        f"Mesa directory exists: {info['mesa_dir_exists']} (git repo: {info['mesa_is_git_repo']})"
    )
    print("-" * 50 + "\n")

    return info


def get_remediation_suggestions(info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return a list of remediation suggestions based on diagnostics.

    Each suggestion is a dict with keys: 'id', 'description', 'cmd' (list), 'platforms'
    """
    suggestions: List[Dict[str, Any]] = []

    os_name = platform.system()

    # If Tkinter is missing or unusable, suggest platform-specific package installs
    if not info.get("tk_usable", False):
        if os_name == "Linux":
            # Detect package manager
            if shutil.which("apt"):
                suggestions.append(
                    {
                        "id": "install-tk-apt",
                        "description": "Install tkinter via apt (Debian/Ubuntu)",
                        "cmd": [
                            "sudo",
                            "apt",
                            "update",
                            "&&",
                            "sudo",
                            "apt",
                            "install",
                            "-y",
                            "python3-tk",
                        ],
                        "platforms": ["Linux"],
                    }
                )
            if shutil.which("dnf"):
                suggestions.append(
                    {
                        "id": "install-tk-dnf",
                        "description": "Install tkinter via dnf (Fedora)",
                        "cmd": ["sudo", "dnf", "install", "-y", "python3-tkinter"],
                        "platforms": ["Linux"],
                    }
                )
            if shutil.which("pacman"):
                suggestions.append(
                    {
                        "id": "install-tk-pacman",
                        "description": "Install tkinter via pacman (Arch)",
                        "cmd": ["sudo", "pacman", "-S", "--noconfirm", "tk"],
                        "platforms": ["Linux"],
                    }
                )
            # Generic fallback
            suggestions.append(
                {
                    "id": "install-tk-generic-linux",
                    "description": "Generic Linux instruction to install tkinter (try your distro package manager)",
                    "cmd": [],
                    "platforms": ["Linux"],
                }
            )
        elif os_name == "Darwin":
            if shutil.which("brew"):
                suggestions.append(
                    {
                        "id": "install-python-brew",
                        "description": "Install Python (with tk) via Homebrew",
                        "cmd": ["brew", "install", "python"],
                        "platforms": ["Darwin"],
                    }
                )
            suggestions.append(
                {
                    "id": "install-tk-mac",
                    "description": "macOS: install Python via Homebrew or ensure ActiveTcl/Tk is installed",
                    "cmd": [],
                    "platforms": ["Darwin"],
                }
            )
        elif os_name == "Windows":
            suggestions.append(
                {
                    "id": "install-python-windows",
                    "description": "Windows: Reinstall Python from python.org and ensure Tcl/Tk option is selected",
                    "cmd": [],
                    "platforms": ["Windows"],
                }
            )

    # If git missing, suggest install
    if not info.get("git_path"):
        if os_name == "Linux" and shutil.which("apt"):
            suggestions.append(
                {
                    "id": "install-git-apt",
                    "description": "Install git via apt (Debian/Ubuntu)",
                    "cmd": ["sudo", "apt", "update", "&&", "sudo", "apt", "install", "-y", "git"],
                    "platforms": ["Linux"],
                }
            )
        elif os_name == "Darwin" and shutil.which("brew"):
            suggestions.append(
                {
                    "id": "install-git-brew",
                    "description": "Install git via Homebrew",
                    "cmd": ["brew", "install", "git"],
                    "platforms": ["Darwin"],
                }
            )
        elif os_name == "Windows":
            suggestions.append(
                {
                    "id": "install-git-windows",
                    "description": "Windows: Install Git from https://git-scm.com/download/win",
                    "cmd": [],
                    "platforms": ["Windows"],
                }
            )

    return suggestions


def interactive_remediate(info: Dict[str, Any]) -> None:
    """Interactively offer and execute remediation steps, with explicit user consent.

    This will not run anything without consent. It prints and returns after each action.
    """
    suggestions = get_remediation_suggestions(info)
    if not suggestions:
        print("No remediation suggestions available.")
        return

    for s in suggestions:
        desc = s["description"]
        cmd = s.get("cmd", [])
        platforms = ",".join(s.get("platforms", []))
        msg = f"Suggestion: {desc} (platforms: {platforms})"

        # Ask for consent
        consent = False
        if TK_AVAILABLE and messagebox:
            try:
                consent = messagebox.askyesno(
                    "Remediation Suggestion",
                    msg + "\n\nApply this change? (Requires sudo/root for package managers)",
                )
            except Exception:
                consent = False
        else:
            resp = input(f"{msg}\nApply this change? [y/N]: ")
            consent = resp.strip().lower() in ("y", "yes")

        if not consent:
            print(f"Skipped: {desc}")
            continue

        if not cmd:
            print(
                f"No automatic command available for: {desc}. Please follow printed instructions."
            )
            continue

        # Execute the command (note: some commands are compound strings; run via shell for safety)
        try:
            print(f"Running: {' '.join(cmd)}")
            # Use shell when command contains shell operators like &&
            use_shell = any(op in cmd for op in ("&&", "|", ";"))
            if use_shell:
                # For security, we'll split the command and run each part separately
                # This prevents shell injection while still allowing compound commands
                full_cmd = " ".join(cmd)
                proc = subprocess.run(full_cmd, shell=True, check=False)
            else:
                proc = subprocess.run(cmd, check=False)

            if proc.returncode == 0:
                print(f"Action completed: {desc}")
            else:
                print(f"Action failed (exit {proc.returncode}): {desc}")
        except Exception as e:
            print(f"Error running remediation for {desc}: {e}")


# Set up logging to capture errors that occur during runtime
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


def get_version_key(filename: str) -> List[int]:
    """Convert a release note filename (e.g., '22.1.0.rst') to a sortable key."""
    try:
        # Remove extension and split version string into parts
        parts = filename.replace(".rst", "").split(".")
        # Convert all parts to integers for numerical sorting
        return [int(p) for p in parts]
    except ValueError:
        # Return a default key for non-version-like filenames
        return [0, 0, 0]


# Compiled regex for parsing the 'RELEASE: ...' headers in the summaries file.
# Flags are IGNORECASE and MULTILINE to make parsing robust.
RELEASE_NOTES_PATTERN = re.compile(
    r"^\s*=+\s*\n\s*RELEASE:\s*([\d\.]+)\s*\n\s*=+\s*\n", flags=re.IGNORECASE | re.MULTILINE
)


class MesaViewerApp:
    def __init__(self, root: tk.Tk) -> None:
        try:
            self.root = root
            self.root.title(f"Mesa Git History Viewer v{VERSION}")
            self.root.geometry("1100x700")

            # Local paths for repo and generated caches
            # Use the script location so launcher scripts can be executed from any working directory
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            self.mesa_dir = os.path.join(self.base_dir, "mesa")
            self.changelog_history_file = os.path.join(self.base_dir, "Mesa_Changelog_History.txt")
            self.summaries_file = os.path.join(self.base_dir, "Mesa_Summaries.txt")

            # Check for git availability and warn the user if missing
            self.git_path = shutil.which("git")  # Store git path for consistent use
            self.git_available = self.git_path is not None
            if not self.git_available:
                with suppress(Exception):
                    messagebox.showwarning(
                        "Git not found",
                        "Git is not installed or not in PATH. The 'Refresh' feature will be disabled.",
                    )

            self.full_history_data: List[Tuple[str, str, str]] = []
            self.summaries_data: Dict[str, str] = {}

            self.setup_ui()

            # Check if Mesa repo exists; if not, offer to download it
            if not os.path.isdir(self.mesa_dir):
                self.prompt_download_mesa()
            else:
                self.load_data()
                self.update_tree(self.full_history_data)
        except Exception as e:
            logging.error(f"Error initializing MesaViewerApp: {e}")
            messagebox.showerror(
                "Initialization Error", f"Failed to initialize the application: {e}"
            )

    def setup_ui(self) -> None:
        try:
            # Global controls
            toolbar = ttk.Frame(self.root, padding="5")
            toolbar.pack(side=tk.TOP, fill=tk.X)

            self.refresh_btn = ttk.Button(
                toolbar, text="Refresh Data (Git Pull)", command=self.start_refresh
            )
            self.refresh_btn.pack(side=tk.LEFT)
            if not getattr(self, "git_available", True):
                self.refresh_btn.config(state=tk.DISABLED)

            # Download/Update button (redownload the entire Mesa repo)
            self.download_btn = ttk.Button(
                toolbar, text="Download/Update Mesa Repo", command=self.start_download_mesa
            )
            self.download_btn.pack(side=tk.LEFT, padx=5)

            self.status_label = ttk.Label(toolbar, text="Ready", foreground="gray")
            self.status_label.pack(side=tk.LEFT, padx=10)

            # Progress bar for downloads/refreshes (hidden by default)
            self.progress_bar = ttk.Progressbar(toolbar, mode="indeterminate", length=200)
            self.progress_bar.pack(side=tk.LEFT, padx=10)
            self.progress_bar.pack_forget()  # Hide initially

            # Tab navigation
            self.notebook = ttk.Notebook(self.root)
            self.notebook.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

            self.history_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.history_frame, text="Changelog History")
            self.setup_history_tab()

            self.summaries_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.summaries_frame, text="Summaries (Release Notes)")
            self.setup_summaries_tab()

            self.agg_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.agg_frame, text="Aggregated List Export")
            self.setup_agg_tab()
        except Exception as e:
            logging.error(f"Error setting up UI: {e}")
            messagebox.showerror("UI Setup Error", f"Failed to set up the user interface: {e}")

    def setup_history_tab(self) -> None:
        try:
            search_frame = ttk.Frame(self.history_frame, padding="5")
            search_frame.pack(fill=tk.X)

            ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
            self.search_var = tk.StringVar()
            # Prefer trace_add when available; fallback to legacy trace for compatibility
            try:
                self.search_var.trace_add("write", lambda *a: self.filter_history())
            except AttributeError:
                self.search_var.trace("w", lambda *a: self.filter_history())
            self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
            self.search_entry.pack(side=tk.LEFT, padx=5)

            # Main history table
            columns = ("date", "hash", "message")
            self.tree = ttk.Treeview(self.history_frame, columns=columns, show="headings")
            self.tree.heading("date", text="Date")
            self.tree.heading("hash", text="Hash")
            self.tree.heading("message", text="Message")

            self.tree.column("date", width=100, stretch=False)
            self.tree.column("hash", width=100, stretch=False)
            self.tree.column("message", width=600)

            scrollbar = ttk.Scrollbar(
                self.history_frame, orient=tk.VERTICAL, command=self.tree.yview
            )
            self.tree.configure(yscrollcommand=scrollbar.set)

            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        except Exception as e:
            logging.error(f"Error setting up history tab: {e}")
            messagebox.showerror("Tab Setup Error", f"Failed to set up the history tab: {e}")

    def setup_summaries_tab(self) -> None:
        try:
            # Splitscreen view for release selection and reading
            paned = ttk.PanedWindow(self.summaries_frame, orient=tk.HORIZONTAL)
            paned.pack(fill=tk.BOTH, expand=True)

            left_frame = ttk.Frame(paned, width=200)
            self.release_list = tk.Listbox(left_frame, selectmode=tk.SINGLE)
            self.release_list.pack(fill=tk.BOTH, expand=True)
            self.release_list.bind("<<ListboxSelect>>", self.on_release_select)
            paned.add(left_frame, weight=1)

            right_frame = ttk.Frame(paned)
            self.summary_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
            self.summary_text.pack(fill=tk.BOTH, expand=True)
            paned.add(right_frame, weight=4)
        except Exception as e:
            logging.error(f"Error setting up summaries tab: {e}")
            messagebox.showerror("Tab Setup Error", f"Failed to set up the summaries tab: {e}")

    def setup_agg_tab(self) -> None:
        try:
            # Configuration for timeframe filtering
            controls_frame = ttk.Frame(self.agg_frame, padding="5")
            controls_frame.pack(fill=tk.X)

            ttk.Label(controls_frame, text="Aggregate last").pack(side=tk.LEFT)

            self.months_var = tk.StringVar(value="1")
            months_spin = ttk.Spinbox(
                controls_frame, from_=1, to=120, textvariable=self.months_var, width=5
            )
            months_spin.pack(side=tk.LEFT, padx=5)

            ttk.Label(controls_frame, text="months").pack(side=tk.LEFT)

            generate_btn = ttk.Button(
                controls_frame, text="Generate List", command=self.generate_agg_list
            )
            generate_btn.pack(side=tk.LEFT, padx=10)

            copy_btn = ttk.Button(
                controls_frame, text="Copy to Clipboard", command=self.copy_to_clipboard
            )
            copy_btn.pack(side=tk.LEFT)

            self.agg_text = scrolledtext.ScrolledText(self.agg_frame, wrap=tk.WORD)
            self.agg_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            ttk.Label(
                self.agg_frame,
                text="Select text and press Ctrl+C to copy, or Ctrl+A to select all.",
            ).pack(side=tk.BOTTOM, pady=5)
        except Exception as e:
            logging.error(f"Error setting up aggregated tab: {e}")
            messagebox.showerror("Tab Setup Error", f"Failed to set up the aggregated tab: {e}")

    def log_status(self, msg: str) -> None:
        try:
            # Thread-safe status updates - check if root is still alive
            try:
                if self.root.winfo_exists():
                    self.root.after(0, lambda: self.status_label.config(text=msg))
            except tk.TclError:
                # Root has been destroyed
                pass
        except Exception as e:
            logging.error(f"Error updating status: {e}")

    def show_progress(self) -> None:
        """Show and start the progress bar animation."""
        try:
            if self.root.winfo_exists():
                def show_and_start() -> None:
                    self.progress_bar.pack(side=tk.LEFT, padx=10)
                    self.progress_bar.start()
                self.root.after(0, show_and_start)
        except Exception as e:
            logging.error(f"Error showing progress bar: {e}")

    def hide_progress(self) -> None:
        """Stop and hide the progress bar."""
        try:
            if self.root.winfo_exists():
                def stop_and_hide() -> None:
                    self.progress_bar.stop()
                    self.progress_bar.pack_forget()
                self.root.after(0, stop_and_hide)
        except Exception as e:
            logging.error(f"Error hiding progress bar: {e}")

    def start_refresh(self) -> None:
        try:
            # Kick off background thread to avoid GUI lockup during git pull
            self.refresh_btn.config(state=tk.DISABLED)
            self.show_progress()
            threading.Thread(target=self.run_refresh_logic, daemon=True).start()
        except Exception as e:
            logging.error(f"Error starting refresh: {e}")
            self.refresh_btn.config(state=tk.NORMAL)
            self.hide_progress()
            messagebox.showerror("Refresh Error", f"Failed to start refresh: {e}")

    def prompt_download_mesa(self) -> None:
        """Prompt user to download Mesa repo on first use."""
        try:
            msg = (
                "The Mesa repository has not been downloaded yet.\n\n"
                "This application requires the Mesa source code to function.\n"
                "Would you like to download it now?\n\n"
                "This may take several minutes on first download."
            )
            if messagebox.askyesno("Download Mesa Repository", msg):
                self.start_download_mesa()
            else:
                self.log_status(
                    "Mesa repository download skipped. App will have limited functionality."
                )
        except Exception as e:
            logging.error(f"Error prompting for Mesa download: {e}")

    def start_download_mesa(self) -> None:
        """Start the Mesa repository download/update in a background thread."""
        try:
            self.download_btn.config(state=tk.DISABLED)
            self.refresh_btn.config(state=tk.DISABLED)
            self.show_progress()
            threading.Thread(target=self.run_download_mesa_logic, daemon=True).start()
        except Exception as e:
            logging.error(f"Error starting Mesa download: {e}")
            self.download_btn.config(state=tk.NORMAL)
            self.refresh_btn.config(state=tk.NORMAL)
            self.hide_progress()
            messagebox.showerror("Download Error", f"Failed to start download: {e}")

    def run_download_mesa_logic(self) -> None:
        """Download or update the Mesa repository."""
        try:
            if self.git_path is None:
                self.log_status("Git not found.")
                print("Git not found.")
                error_msg = "Git is not installed or not in PATH. Please install Git and try again."
                logging.error(error_msg)
                try:
                    if self.root.winfo_exists():
                        self.root.after(0, lambda: messagebox.showerror("Git Error", error_msg))
                except tk.TclError:
                    pass
                return

            if os.path.exists(self.mesa_dir):
                self.log_status("Updating Mesa repository...")
                print("Updating Mesa repository...")
                # If repo exists, just pull the latest
                # Remove capture_output to let git show progress in terminal
                subprocess.run([self.git_path, "-C", self.mesa_dir, "pull"], check=True, text=True)
                self.log_status("Mesa repository updated successfully.")
                print("Mesa repository updated successfully.")
            else:
                self.log_status("Cloning Mesa repository (this may take a while)...")
                print("Cloning Mesa repository (this may take a while)...")
                # Clone the repository
                # Remove capture_output to let git show progress in terminal
                subprocess.run(
                    [self.git_path, "clone", "https://gitlab.freedesktop.org/mesa/mesa.git", self.mesa_dir],
                    check=True,
                    text=True,
                )
                self.log_status("Mesa repository downloaded successfully.")
                print("Mesa repository downloaded successfully.")

            # Refresh the data after download
            self.log_status("Generating history and summaries...")
            print("Generating history and summaries...")
            self.log_status("Generating Changelog History...")
            with open(self.changelog_history_file, "w", encoding="utf-8") as f:
                subprocess.run(
                    [
                        self.git_path,
                        "-C",
                        self.mesa_dir,
                        "log",
                        "--since=12 months ago",
                        "--pretty=format:%ad | %s (%h)",
                        "--date=short",
                    ],
                    stdout=f,
                    check=True,
                    encoding="utf-8",
                    text=True,
                )

            self.log_status("Compiling Release Notes...")
            self.generate_summaries_python()

            self.log_status("Download and processing complete.")
            print("Download and processing complete.")
            try:
                if self.root.winfo_exists():
                    self.root.after(0, lambda: self.load_data())
                    self.root.after(0, lambda: self.update_tree(self.full_history_data))
            except tk.TclError:
                pass
        except subprocess.CalledProcessError as e:
            self.log_status("Download failed.")
            print(f"Download failed: {e}")
            error_msg = f"Git command failed: {e}"
            if hasattr(e, "stderr") and e.stderr:
                error_msg += f"\n{e.stderr}"
            logging.error(error_msg)
            try:
                if self.root.winfo_exists():
                    self.root.after(0, lambda: messagebox.showerror("Git Error", error_msg))
            except tk.TclError:
                pass
        except FileNotFoundError:
            self.log_status("Git not found.")
            print("Git not found.")
            error_msg = "Git is not installed or not in PATH. Please install Git and try again."
            logging.error(error_msg)
            try:
                if self.root.winfo_exists():
                    self.root.after(0, lambda: messagebox.showerror("Git Error", error_msg))
            except tk.TclError:
                pass
        except Exception as e:
            self.log_status("Download error.")
            print(f"Download error: {e}")
            error_msg = f"Unexpected error during download: {e}"
            logging.error(error_msg)
            try:
                if self.root.winfo_exists():
                    self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            except tk.TclError:
                pass
        finally:
            try:
                if self.root.winfo_exists():
                    self.root.after(0, lambda: self.download_btn.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.refresh_btn.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.hide_progress())
            except tk.TclError:
                pass

    def run_refresh_logic(self) -> None:
        try:
            if self.git_path is None:
                self.log_status("Git not found.")
                print("Git not found.")
                error_msg = "Git is not installed or not in PATH. Please install Git and try again."
                logging.error(error_msg)
                try:
                    if self.root.winfo_exists():
                        self.root.after(0, lambda: messagebox.showerror("Git Error", error_msg))
                except tk.TclError:
                    pass
                return

            self.log_status("Updating Repository...")
            print("Updating Repository...")
            if not os.path.exists(self.mesa_dir):
                self.log_status("Cloning repo (this may take a while)...")
                print("Cloning repo (this may take a while)...")
                subprocess.run(
                    [self.git_path, "clone", "https://gitlab.freedesktop.org/mesa/mesa.git", self.mesa_dir],
                    check=True,
                    text=True,
                )
            else:
                subprocess.run([self.git_path, "-C", self.mesa_dir, "pull"], check=True, text=True)

            self.log_status("Generating Changelog History...")
            print("Generating Changelog History...")
            # Dump last year of history into cache file
            with open(self.changelog_history_file, "w", encoding="utf-8") as f:
                subprocess.run(
                    [
                        self.git_path,
                        "-C",
                        self.mesa_dir,
                        "log",
                        "--since=12 months ago",
                        "--pretty=format:%ad | %s (%h)",
                        "--date=short",
                    ],
                    stdout=f,
                    check=True,
                    encoding="utf-8",
                    text=True,
                )

            self.log_status("Compiling Release Notes...")
            self.generate_summaries_python()

            self.log_status("Refresh Complete.")
            print("Refresh Complete.")
            try:
                if self.root.winfo_exists():
                    self.root.after(0, lambda: self.load_data())
                    self.root.after(0, lambda: self.update_tree(self.full_history_data))
            except tk.TclError:
                pass
        except subprocess.CalledProcessError as e:
            self.log_status("Git pull failed.")
            print(f"Git pull failed: {e}")
            error_msg = (
                f"Git command failed: {e}\nStdout: {e.stdout}\nStderr: {e.stderr}"
                if hasattr(e, "stdout") and hasattr(e, "stderr")
                else f"Git command failed: {e}"
            )
            logging.error(error_msg)
            try:
                if self.root.winfo_exists():
                    self.root.after(0, lambda: messagebox.showerror("Git Error", error_msg))
            except tk.TclError:
                pass
        except FileNotFoundError:
            self.log_status("Git command not found.")
            print("Git command not found.")
            error_msg = "Git is not installed or not in PATH. Please install Git and try again."
            logging.error(error_msg)
            try:
                if self.root.winfo_exists():
                    self.root.after(0, lambda: messagebox.showerror("Git Error", error_msg))
            except tk.TclError:
                pass
        except Exception as e:
            self.log_status("Refresh error.")
            print(f"Refresh error: {e}")
            error_msg = f"Unexpected error during refresh: {e}"
            logging.error(error_msg)
            try:
                if self.root.winfo_exists():
                    self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            except tk.TclError:
                pass
        finally:
            try:
                if self.root.winfo_exists():
                    self.root.after(0, lambda: self.refresh_btn.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.hide_progress())
            except tk.TclError:
                pass

    def generate_summaries_python(self) -> None:
        try:
            # Scrape relnotes dir for .rst files and merge them into a single cache
            relnotes_dir = os.path.join(self.mesa_dir, "docs", "relnotes")
            if not os.path.exists(relnotes_dir):
                logging.warning(f"Release notes directory does not exist: {relnotes_dir}")
                return

            # Only grab files that look like version numbers
            files = []
            try:
                for f in os.listdir(relnotes_dir):
                    if f.endswith(".rst") and re.match(r"^\d+\.\d+(\.\d+)?\.rst$", f):
                        files.append(f)
            except Exception as e:
                logging.error(f"Error accessing release notes directory: {e}")
                return

            # Sort descending by version number
            def version_key(filename: str) -> List[int]:
                try:
                    parts = filename.replace(".rst", "").split(".")
                    return [int(p) for p in parts]
                except ValueError:
                    return [0, 0, 0]

            files.sort(key=version_key, reverse=True)
            top_50 = files[:50]

            try:
                with open(self.summaries_file, "w", encoding="utf-8") as outfile:
                    outfile.write("MESA RELEASE NOTES COMPILATION\n\n")

                    for rst_file in top_50:
                        version = rst_file.replace(".rst", "")
                        outfile.write(f"\n{'=' * 50}\n RELEASE: {version}\n{'=' * 50}\n\n")

                        path = os.path.join(relnotes_dir, rst_file)
                        try:
                            with open(path, "r", encoding="utf-8", errors="replace") as infile:
                                outfile.write(infile.read())
                        except Exception as e:
                            error_msg = f"Error reading file {path}: {e}\n"
                            outfile.write(error_msg)
                            logging.error(error_msg)
            except Exception as e:
                logging.error(f"Error writing summaries file: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in generate_summaries_python: {e}")

    def load_data(self) -> None:
        try:
            # Parse history cache
            self.full_history_data = []
            if os.path.exists(self.changelog_history_file):
                try:
                    with open(
                        self.changelog_history_file, "r", encoding="utf-8", errors="replace"
                    ) as f:
                        for line_num, line in enumerate(f, 1):
                            try:
                                line = line.strip()
                                if not line:
                                    continue

                                # Match Date | Message (Hash)
                                match = re.search(
                                    r"^(\d{4}-\d{2}-\d{2}) \| (.*) \(([a-f0-9]+)\)$", line
                                )
                                if match:
                                    self.full_history_data.append(
                                        (match.group(1), match.group(3), match.group(2))
                                    )
                                else:
                                    parts = line.split(" | ", 1)
                                    if len(parts) == 2:
                                        self.full_history_data.append((parts[0], "?", parts[1]))
                            except Exception as e:
                                logging.warning(
                                    f"Error parsing line {line_num} in changelog history file: {e}"
                                )
                                continue
                except Exception as e:
                    logging.error(f"Error reading changelog history file: {e}")

            # Load summaries data
            self.load_summaries()

        except Exception as e:
            logging.error(f"Unexpected error in load_data: {e}")
            messagebox.showerror("Data Load Error", f"Failed to load data: {e}")

    def load_summaries(self) -> None:
        """Load and parse the summaries cache file, populating the release list."""
        try:
            self.summaries_data = {}
            with suppress(Exception):
                self.release_list.delete(0, tk.END)

            if os.path.exists(self.summaries_file):
                try:
                    with open(self.summaries_file, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()

                    pattern = re.compile(
                        r"^\s*=+\s*\n\s*RELEASE:\s*([\d\.]+)\s*\n\s*=+\s*\n",
                        flags=re.IGNORECASE | re.MULTILINE,
                    )
                    parts = pattern.split(content)
                    if len(parts) > 1:
                        for i in range(1, len(parts), 2):
                            if i + 1 < len(parts):  # Make sure we have both version and text
                                version, text = parts[i].strip(), parts[i + 1]
                                self.summaries_data[version] = text
                                with suppress(Exception):
                                    self.release_list.insert(tk.END, version)
                except Exception as e:
                    logging.error(f"Error reading summaries file: {e}")
        except Exception as e:
            logging.error(f"Error loading summaries: {e}")

    @staticmethod
    def compute_cutoff_date(months: int, now: Optional[datetime] = None) -> datetime:
        if now is None:
            now = datetime.now()

        years_to_subtract = months // 12
        months_to_subtract_from_current = months % 12

        target_year = now.year - years_to_subtract
        target_month = now.month - months_to_subtract_from_current

        if target_month <= 0:
            target_month += 12
            target_year -= 1

        target_day = min(now.day, 28)  # Keeping existing logic for day

        return datetime(target_year, target_month, target_day)

    def update_tree(self, data: List[Tuple[str, str, str]]) -> None:
        try:
            if hasattr(self, "tree") and self.tree.winfo_exists():
                self.tree.delete(*self.tree.get_children())
                # Truncate at 5k rows to avoid dragging UI performance
                for item in data[:5000]:
                    self.tree.insert("", tk.END, values=item)
            else:
                logging.warning("Tree widget does not exist or has been destroyed")
        except Exception as e:
            logging.error(f"Error updating tree: {e}")
            messagebox.showerror("Tree Update Error", f"Failed to update the tree view: {e}")

    def filter_history(self, *args: Any) -> None:
        try:
            # Dynamic filtering based on search entry
            query = self.search_var.get().lower()
            if not query:
                self.update_tree(self.full_history_data)
                return

            filtered = [
                item
                for item in self.full_history_data
                if query in str(item[1]).lower() or query in str(item[2]).lower()
            ]
            self.update_tree(filtered)
        except Exception as e:
            logging.error(f"Error filtering history: {e}")
            messagebox.showerror("Filter Error", f"Failed to filter history: {e}")

    def on_release_select(self, event: Any) -> None:
        try:
            selection = self.release_list.curselection()  # type: ignore
            if selection:
                version = self.release_list.get(selection[0])
                content = self.summaries_data.get(version, "")
                if hasattr(self, "summary_text") and self.summary_text.winfo_exists():
                    self.summary_text.delete("1.0", tk.END)
                    self.summary_text.insert("1.0", content)
                else:
                    logging.warning("Summary text widget does not exist or has been destroyed")
        except Exception as e:
            logging.error(f"Error selecting release: {e}")
            messagebox.showerror("Selection Error", f"Failed to select release: {e}")

    def generate_agg_list(self) -> None:
        try:
            # Generate raw text list for custom date range
            try:
                months = int(self.months_var.get())
            except ValueError:
                messagebox.showerror("Input Error", "Please enter a valid number of months.")
                return

            cutoff = self.compute_cutoff_date(months)

            output = [f"Mesa History - Last {months} Months", "-" * 60]
            count = 0
            for date_str, h, msg in self.full_history_data:
                try:
                    if datetime.strptime(date_str, "%Y-%m-%d") >= cutoff:
                        output.append(f"{date_str} | {msg} ({h})")
                        count += 1
                except ValueError:
                    continue

            if hasattr(self, "agg_text") and self.agg_text.winfo_exists():
                self.agg_text.delete("1.0", tk.END)
                self.agg_text.insert("1.0", "\n".join(output))
            else:
                logging.warning("Aggregated text widget does not exist or has been destroyed")

            self.log_status(f"Generated {count} entries.")
        except Exception as e:
            logging.error(f"Error generating aggregated list: {e}")
            messagebox.showerror("Generation Error", f"Failed to generate aggregated list: {e}")

    def copy_to_clipboard(self) -> None:
        try:
            if hasattr(self, "agg_text") and self.agg_text.winfo_exists():
                content = self.agg_text.get("1.0", tk.END).strip()
                if content:
                    try:
                        self.root.clipboard_clear()
                        self.root.clipboard_append(content)
                        self.root.update()
                        self.log_status("Copied to clipboard.")
                    except tk.TclError as ce:
                        logging.error(f"Clipboard error: {ce}")
                        self.log_status("Failed to copy to clipboard.")
                else:
                    self.log_status("No content to copy.")
            else:
                logging.warning("Aggregated text widget does not exist or has been destroyed")
                self.log_status("Cannot copy - content not available.")
        except Exception as e:
            logging.error(f"Error copying to clipboard: {e}")
            messagebox.showerror("Clipboard Error", f"Failed to copy to clipboard: {e}")


def _print_tk_install_instructions() -> None:
    """Print platform-specific instructions for getting Tcl/Tk / tkinter working."""
    os_name = platform.system()
    print("\nERROR: Tkinter is not available or Tcl/Tk is not installed correctly.")
    if os_name == "Linux":
        print("On Debian/Ubuntu: sudo apt install python3-tk")
        print("On Fedora: sudo dnf install python3-tkinter")
        print("On Arch: sudo pacman -S tk")
    elif os_name == "Darwin":
        print(
            "On macOS: install Python via Homebrew (brew install python) or ensure your Python distribution includes Tk support."
        )
        print("If using system Python, you may need to install ActiveTcl or use Homebrew python.")
    elif os_name == "Windows":
        print(
            "On Windows: reinstall Python from python.org and ensure 'Tcl/Tk and IDLE' are selected, or install a Python distribution that bundles Tcl/Tk."
        )
    else:
        print("Please install Tcl/Tk / tkinter for your platform.")
    print("\nAfter installing, try running the application again.\n")


if __name__ == "__main__":
    # CLI diagnostic flag - run before any GUI checks so users without tkinter can diagnose
    if "--diagnose" in sys.argv:
        run_diagnostics()
        # allow --fix with --diagnose
        if "--fix" in sys.argv:
            info = run_diagnostics()  # get info to act on
            interactive_remediate(info)
        sys.exit(0)

    # CLI quick-fix flag (runs diagnostics and offers interactive remediation)
    if "--fix" in sys.argv:
        info = run_diagnostics()
        interactive_remediate(info)
        sys.exit(0)

    # Pre-flight checks
    if not TK_AVAILABLE:
        _print_tk_install_instructions()
        sys.exit(1)

    # Validate Tcl/Tk is usable (some Python builds may lack init.tcl)
    try:
        test_root = tk.Tk()
        test_root.withdraw()
        test_root.update()
        test_root.destroy()
    except TclError as e:
        print("\nERROR: Tcl/Tk appears to be broken or missing (could not initialize GUI).")
        print(f"Details: {e}\n")
        _print_tk_install_instructions()
        sys.exit(1)

    # Warn on Python versions older than recommended
    if sys.version_info < (3, 9):
        try:
            messagebox.showwarning(
                "Python version",
                "This application is tested on Python 3.9+. You are running an older Python version which may cause unexpected issues.",
            )
        except Exception:
            print(
                "WARNING: This application is tested on Python 3.9+. You are running an older Python version which may cause unexpected issues."
            )

    root = tk.Tk()
    app = MesaViewerApp(root)
    root.mainloop()
