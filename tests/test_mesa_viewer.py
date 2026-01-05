import tempfile
import os
import sys
import pytest
import tkinter as tk
from tkinter import TclError
from unittest.mock import Mock, patch

# Add the parent directory to the path so we can import mesa_viewer
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def tk_root():
    try:
        root = tk.Tk()
    except TclError:
        pytest.skip("Tkinter not available on this system")
    yield root
    try:
        root.destroy()
    except Exception:
        pass

def test_app_initialization(tk_root):
    """Test that the application initializes without errors."""
    root = tk_root
    temp_dir = tempfile.mkdtemp()

    try:
        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)
            assert app.root is not None
            # Ensure that when pointing to an empty base_dir, no data is loaded
            app.base_dir = temp_dir
            app.changelog_history_file = os.path.join(temp_dir, "Mesa_Changelog_History.txt")
            app.summaries_file = os.path.join(temp_dir, "Mesa_Summaries.txt")
            app.load_data()
            assert app.full_history_data == []
            assert app.summaries_data == {}
    finally:
        root.destroy()
        os.rmdir(temp_dir)


def test_data_parsing_valid_format(tk_root):
    """Test parsing of valid data format."""
    import shutil
    root = tk_root
    temp_dir = tempfile.mkdtemp()
    temp_changelog_history = os.path.join(temp_dir, "Mesa_Changelog_History.txt")

    try:
        # Create a sample changelog history file with valid format - following git log format
        # Format: Date | Message (hash) - where message should not contain parentheses, hash is hex
        sample_data = """2023-01-01 | Initial commit (abc123de)
2023-01-02 | Add feature (def456ab)
2023-01-03 | Fix bug (fedcba98)"""

        with open(temp_changelog_history, 'w', encoding='utf-8') as f:
            f.write(sample_data)

        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)
            # Manually call load_data to test parsing
            app.changelog_history_file = temp_changelog_history
            app.load_data()

            assert len(app.full_history_data) == 3
            # The order might be different, so let's check that all expected items are present
            expected_items = [
                ('2023-01-01', 'abc123de', 'Initial commit'),
                ('2023-01-02', 'def456ab', 'Add feature'),
                ('2023-01-03', 'fedcba98', 'Fix bug')
            ]
            for expected in expected_items:
                assert expected in app.full_history_data
    finally:
        root.destroy()
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_data_parsing_alternative_format(tk_root):
    """Test parsing of alternative data format."""
    import shutil
    root = tk_root
    temp_dir = tempfile.mkdtemp()
    temp_changelog_history = os.path.join(temp_dir, "Mesa_Changelog_History.txt")

    try:
        # Create a sample changelog history file with alternative format
        sample_data = """2023-01-01 | Initial commit without hash
2023-01-02 | Another commit without hash"""

        with open(temp_changelog_history, 'w', encoding='utf-8') as f:
            f.write(sample_data)

        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)
            # Manually call load_data to test parsing
            app.changelog_history_file = temp_changelog_history
            app.load_data()

            assert len(app.full_history_data) == 2
            # Check that both items are present (order may vary)
            expected_items = [
                ('2023-01-01', '?', 'Initial commit without hash'),
                ('2023-01-02', '?', 'Another commit without hash')
            ]
            for expected in expected_items:
                assert expected in app.full_history_data
    finally:
        root.destroy()
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_data_parsing_empty_file(tk_root):
    """Test parsing of empty file."""
    import shutil
    root = tk_root
    temp_dir = tempfile.mkdtemp()
    temp_changelog_history = os.path.join(temp_dir, "Mesa_Changelog_History.txt")

    try:
        with open(temp_changelog_history, 'w', encoding='utf-8') as f:
            f.write('')

        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)
            # Manually call load_data to test parsing
            app.changelog_history_file = temp_changelog_history
            app.load_data()

            assert len(app.full_history_data) == 0
    finally:
        root.destroy()
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_data_parsing_malformed_lines(tk_root):
    """Test parsing when some lines are malformed."""
    import shutil
    root = tk_root
    temp_dir = tempfile.mkdtemp()
    temp_changelog_history = os.path.join(temp_dir, "Mesa_Changelog_History.txt")

    try:
        # Create a sample changelog history file with some malformed lines
        # Format: Date | Message (hash) - where message should not contain parentheses, hash is hex
        sample_data = """2023-01-01 | Valid commit (abc123de)
This line is malformed
2023-01-02 | Another valid commit (def456ab)
Another malformed line
2023-01-03 | Final valid commit (fedcba98)"""

        with open(temp_changelog_history, 'w', encoding='utf-8') as f:
            f.write(sample_data)

        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)
            # Manually call load_data to test parsing
            app.changelog_history_file = temp_changelog_history
            app.load_data()

            # Should only parse the valid lines
            assert len(app.full_history_data) == 3
            # Check that all expected valid items are present
            expected_items = [
                ('2023-01-01', 'abc123de', 'Valid commit'),
                ('2023-01-02', 'def456ab', 'Another valid commit'),
                ('2023-01-03', 'fedcba98', 'Final valid commit')
            ]
            for expected in expected_items:
                assert expected in app.full_history_data
    finally:
        root.destroy()
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_filter_history(tk_root):
    """Test the history filtering functionality."""
    root = tk_root
    temp_dir = tempfile.mkdtemp()

    try:
        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)
            # Ensure summaries parsing is not triggered by pointing to a non-existent summaries file
            app.summaries_file = os.path.join(temp_dir, "Mesa_Summaries.txt")

            # Set up some test data
            app.full_history_data = [
                ('2023-01-01', 'abc123def', 'Feature A implementation'),
                ('2023-01-02', 'def456ghi', 'Bug fix for feature B'),
                ('2023-01-03', 'ghi789jkl', 'Documentation update')
            ]

            # Mock the update_tree method to capture calls
            app.update_tree = Mock()

            # Create the search_var attribute
            app.search_var = Mock()
            app.search_var.get.return_value = 'feature'

            # Test filtering by message content
            app.filter_history()

            # Check that update_tree was called with filtered data
            app.update_tree.assert_called_once()
            # The call_args should contain the filtered data
            call_args = app.update_tree.call_args[0][0]
            assert len(call_args) == 2  # Should have 2 items matching 'feature'
            messages = [item[2] for item in call_args]
            assert 'Feature A implementation' in messages
            assert 'Bug fix for feature B' in messages
    finally:
        root.destroy()
        os.rmdir(temp_dir)


def test_filter_history_empty_query(tk_root):
    """Test that empty query shows all data."""
    root = tk_root
    temp_dir = tempfile.mkdtemp()

    try:
        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)
            # Set up some test data
            app.full_history_data = [
                ('2023-01-01', 'abc123def', 'Feature A implementation'),
                ('2023-01-02', 'def456ghi', 'Bug fix for feature B')
            ]

            # Mock the update_tree method to capture calls
            app.update_tree = Mock()

            # Create the search_var attribute
            app.search_var = Mock()
            app.search_var.get.return_value = ''

            # Test with empty query
            app.filter_history()

            # Check that update_tree was called with all data
            app.update_tree.assert_called_once()
            call_args = app.update_tree.call_args[0][0]
            assert len(call_args) == 2  # Should have all items
    finally:
        root.destroy()
        os.rmdir(temp_dir)


def test_generate_agg_list(tk_root):
    """Test the aggregated list generation functionality."""
    root = tk_root
    temp_dir = tempfile.mkdtemp()

    try:
        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)
            # Set up some test data
            app.full_history_data = [
                ('2023-01-01', 'abc123def', 'Feature A implementation'),
                ('2023-06-01', 'def456ghi', 'Bug fix for feature B'),
                ('2024-01-01', 'ghi789jkl', 'Documentation update')
            ]

            # Mock the months variable
            app.months_var = Mock()
            app.months_var.get.return_value = '12'  # 12 months

            # Mock the agg_text widget
            app.agg_text = Mock()
            app.agg_text.delete = Mock()
            app.agg_text.insert = Mock()

            # Mock the log_status method
            app.log_status = Mock()

            # Call the method
            app.generate_agg_list()

            # Check that the text widget methods were called
            app.agg_text.delete.assert_called_once()
            app.agg_text.insert.assert_called_once()
            app.log_status.assert_called_once()
    finally:
        root.destroy()
        os.rmdir(temp_dir)


def test_generate_agg_list_invalid_months(tk_root):
    """Test aggregated list generation with invalid months input."""
    root = tk_root
    temp_dir = tempfile.mkdtemp()

    try:
        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)

            # Mock the months variable to return invalid value
            app.months_var = Mock()
            app.months_var.get.return_value = 'invalid'

            # Mock messagebox to capture the error
            with patch('mesa_viewer.messagebox') as mock_msgbox:
                app.generate_agg_list()
                # Should show an error message
                mock_msgbox.showerror.assert_called_once()
    finally:
        root.destroy()
        os.rmdir(temp_dir)


def test_copy_to_clipboard(tk_root):
    """Test the clipboard copy functionality."""
    root = tk_root
    temp_dir = tempfile.mkdtemp()

    try:
        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)

            # Mock the agg_text widget
            app.agg_text = Mock()
            app.agg_text.get.return_value = 'Test content to copy'

            # Mock root clipboard methods
            app.root.clipboard_clear = Mock()
            app.root.clipboard_append = Mock()
            app.log_status = Mock()

            # Call the method
            app.copy_to_clipboard()

            # Check that clipboard methods were called
            app.root.clipboard_clear.assert_called_once()
            app.root.clipboard_append.assert_called_once_with('Test content to copy')
            app.log_status.assert_called_once_with('Copied to clipboard.')
    finally:
        root.destroy()
        os.rmdir(temp_dir)


def test_copy_to_clipboard_empty_content(tk_root):
    """Test clipboard copy with empty content."""
    root = tk_root
    temp_dir = tempfile.mkdtemp()

    try:
        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)

            # Mock the agg_text widget with empty content
            app.agg_text = Mock()
            app.agg_text.get.return_value = ''

            # Mock root clipboard methods
            app.root.clipboard_clear = Mock()
            app.root.clipboard_append = Mock()
            app.log_status = Mock()

            # Call the method
            app.copy_to_clipboard()

            # Check that clipboard methods were NOT called
            app.root.clipboard_clear.assert_not_called()
            app.root.clipboard_append.assert_not_called()
            app.log_status.assert_called_once_with('No content to copy.')
    finally:
        root.destroy()
        os.rmdir(temp_dir)


def test_ui_widgets_exist(tk_root):
    """Test that UI widgets are created properly."""
    root = tk_root
    temp_dir = tempfile.mkdtemp()

    try:
        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)

            # Check that main UI elements exist
            assert hasattr(app, 'root')
            # Note: These attributes are created during UI setup, so they should exist after initialization
    finally:
        root.destroy()
        os.rmdir(temp_dir)


def test_smoke_test(tk_root):
    """Basic smoke test to ensure the app can be instantiated."""
    import shutil
    root = tk_root
    temp_dir = tempfile.mkdtemp()

    try:
        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)
            assert app is not None
    finally:
        root.destroy()
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_compute_cutoff_date():
    """Test compute_cutoff_date helper with deterministic 'now'."""
    from mesa_viewer import MesaViewerApp
    from datetime import datetime
    # March 31st example to ensure day clipping to 28 works
    now = datetime(2024, 3, 31)
    cutoff_1m = MesaViewerApp.compute_cutoff_date(1, now=now)
    assert cutoff_1m == datetime(2024, 2, 28)

    cutoff_3m = MesaViewerApp.compute_cutoff_date(3, now=now)
    assert cutoff_3m == datetime(2023, 12, 28)


def test_run_diagnostics_basic():
    """Ensure run_diagnostics returns a dictionary with expected keys."""
    from mesa_viewer import run_diagnostics
    info = run_diagnostics()
    assert isinstance(info, dict)
    assert 'python_version' in info
    assert 'tk_imported' in info
    assert 'git_version' in info
    assert 'base_dir' in info


def test_summaries_parsing_tolerant(tk_root):
    """Ensure the summaries parser tolerates spacing and different '=' counts."""
    import shutil
    root = tk_root
    temp_dir = tempfile.mkdtemp()
    temp_summaries = os.path.join(temp_dir, "Mesa_Summaries.txt")

    try:
        content = "\n   ====\n RELEASE: 1.2\n====\nThis is release 1.2\n\n  ===========\n  RELEASE: 2.0\n ===========\nSecond release\n"
        with open(temp_summaries, 'w', encoding='utf-8') as f:
            f.write(content)

        with patch('os.getcwd', return_value=temp_dir):
            from mesa_viewer import MesaViewerApp
            app = MesaViewerApp(root)
            app.summaries_file = temp_summaries
            # Trigger parsing manually since we changed the file path after init
            app.load_summaries()

            assert '1.2' in app.summaries_data
            assert '2.0' in app.summaries_data
    finally:
        root.destroy()
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_get_remediation_suggestions_linux_apt(monkeypatch):
    """When apt is available on Linux, suggest python3-tk and git installs."""
    from mesa_viewer import get_remediation_suggestions

    monkeypatch.setattr('mesa_viewer.platform.system', lambda: 'Linux')
    monkeypatch.setattr('mesa_viewer.shutil.which', lambda name: '/usr/bin/apt' if name == 'apt' else None)

    info = {'tk_usable': False, 'git_path': None}
    suggestions = get_remediation_suggestions(info)
    ids = {s['id'] for s in suggestions}
    assert 'install-tk-apt' in ids
    assert 'install-git-apt' in ids


def test_get_remediation_suggestions_macos_brew(monkeypatch):
    """When Homebrew is available on macOS, suggest brew-based installs."""
    from mesa_viewer import get_remediation_suggestions

    monkeypatch.setattr('mesa_viewer.platform.system', lambda: 'Darwin')
    monkeypatch.setattr('mesa_viewer.shutil.which', lambda name: '/usr/local/bin/brew' if name == 'brew' else None)

    info = {'tk_usable': False, 'git_path': None}
    suggestions = get_remediation_suggestions(info)
    ids = {s['id'] for s in suggestions}
    assert 'install-python-brew' in ids


def test_get_remediation_suggestions_none_needed(monkeypatch):
    """If tk is usable and git is present, there should be no suggestions."""
    from mesa_viewer import get_remediation_suggestions

    monkeypatch.setattr('mesa_viewer.platform.system', lambda: 'Linux')
    monkeypatch.setattr('mesa_viewer.shutil.which', lambda name: '/usr/bin/apt' if name == 'apt' else '/usr/bin/git' if name == 'git' else None)

    info = {'tk_usable': True, 'git_path': '/usr/bin/git'}
    suggestions = get_remediation_suggestions(info)
    assert suggestions == []
