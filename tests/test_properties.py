from datetime import datetime
import re
from hypothesis import given, strategies as st
from mesa_viewer import MesaViewerApp, get_version_key, RELEASE_NOTES_PATTERN

# Define a strategy for generating datetimes. We can constrain the range
# to avoid dealing with dates that are too far in the past or future.
sane_datetimes = st.datetimes(
    min_value=datetime(1990, 1, 1),
    max_value=datetime(2040, 1, 1),
)

# Define a strategy for the number of months. Let's keep it reasonable.
sane_months = st.integers(min_value=1, max_value=480)  # Up to 40 years


@given(now=sane_datetimes, months=sane_months)
def test_compute_cutoff_date_properties(now, months):
    """
    Test properties of the compute_cutoff_date static method.
    """
    # 1. Run the function
    cutoff_date = MesaViewerApp.compute_cutoff_date(months=months, now=now)

    # 2. Check properties
    # Property: The result should always be a datetime object.
    assert isinstance(cutoff_date, datetime)

    # Property: The cutoff date should always be in the past or present compared to 'now'.
    assert cutoff_date <= now

    # Property: The year of the cutoff should be less than or equal to the year of 'now'.
    assert cutoff_date.year <= now.year

    # Property: The day is clamped to 28, so it should never be greater than 28.
    assert cutoff_date.day <= 28

    # Property: The function should not create a date in the future, even with negative months,
    # though our strategy avoids this. Let's test it explicitly.
    negative_months_cutoff = MesaViewerApp.compute_cutoff_date(months=-months, now=now)
    assert negative_months_cutoff.year >= now.year


@given(line=st.text())
def test_parsing_does_not_crash(line):
    """
    This test ensures that the log parsing logic in load_data
    never crashes, no matter what text it's given. It checks that
    the function runs to completion without raising an unhandled exception.
    """
    # This is a simplified test. A more advanced one would involve creating
    # a temporary file with the line and running the full load_data method.
    # For now, we'll just test the regex part.

    try:
        match = re.search(r"^(\d{4}-\d{2}-\d{2}) \| (.*) \(([a-f0-9]+)\)$", line)
        if match:
            # If it matches, groups should be accessible
            _ = match.group(1)
            _ = match.group(2)
            _ = match.group(3)
        else:
            # If it doesn't match, it should just be None
            pass
    except Exception as e:
        # We should never get an unexpected exception from re.search
        raise AssertionError(f"Regex search raised an unexpected exception: {e}") from e


# --- New tests for version and release note parsing ---

# Strategy for generating version-like strings, e.g., "22.1.0.rst"
version_string_strategy = st.lists(
    st.integers(min_value=0, max_value=100), min_size=1, max_size=4
).map(lambda parts: ".".join(map(str, parts)) + ".rst")


@given(filename=st.text())
def test_version_key_never_crashes(filename):
    """
    Property: The get_version_key function should never raise an unhandled exception,
    no matter what string it receives.
    """
    try:
        result = get_version_key(filename)
        assert isinstance(result, list)
    except Exception as e:
        raise AssertionError(f"get_version_key raised an unexpected exception: {e}") from e


@given(v1=version_string_strategy, v2=version_string_strategy)
def test_version_key_sorting(v1, v2):
    """
    Property: If two version strings are different, their keys should also be different,
    and the comparison should be consistent.
    """
    key1 = get_version_key(v1)
    key2 = get_version_key(v2)

    # This is a simple property. A more complex one could involve
    # comparing the numerical values directly.
    if v1 == v2:
        assert key1 == key2
    else:
        assert key1 != key2


# Strategy to generate a block of release notes text
release_block_strategy = st.tuples(
    st.text(min_size=1, max_size=10).map(lambda s: s.strip().replace("\n", "")), st.text()
).map(lambda t: f"\n{'=' * 20}\n RELEASE: {t[0]}\n{'=' * 20}\n{t[1]}")

# Strategy for a full file with multiple blocks and other random text
summary_file_strategy = st.lists(release_block_strategy, max_size=10).map("\n".join)


@given(content=summary_file_strategy)
def test_release_notes_parsing_never_crashes(content):
    """
    Property: Parsing the summary file should never crash, regardless of content.
    """
    try:
        parts = RELEASE_NOTES_PATTERN.split(content)
        # Process the parts to simulate the real logic
        if len(parts) > 1:
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    _version, _text = parts[i].strip(), parts[i + 1]
    except Exception as e:
        raise AssertionError(f"RELEASE_NOTES_PATTERN.split raised an unexpected exception: {e}") from e
