"""
Tests for datetime utility functions.
"""

import sys
from datetime import timedelta
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from plex_music_ratings_sync.util.datetime import format_time


class TestFormatTime:
    """Test the format_time function."""

    def test_hours_minutes_seconds(self):
        """Test formatting with hours, minutes, and seconds."""
        td = timedelta(hours=2, minutes=30, seconds=45)
        assert format_time(td) == "2h 30m 45s"

    def test_one_hour(self):
        """Test formatting with exactly one hour."""
        td = timedelta(hours=1)
        assert format_time(td) == "1h 0m 0s"

    def test_minutes_seconds(self):
        """Test formatting with minutes and seconds only."""
        td = timedelta(minutes=15, seconds=30)
        assert format_time(td) == "15m 30s"

    def test_one_minute(self):
        """Test formatting with exactly one minute."""
        td = timedelta(minutes=1)
        assert format_time(td) == "1m 0s"

    def test_seconds_with_milliseconds(self):
        """Test formatting with seconds and milliseconds."""
        td = timedelta(seconds=5, milliseconds=123)
        assert format_time(td) == "5.123s"

    def test_seconds_only(self):
        """Test formatting with seconds only (no milliseconds)."""
        td = timedelta(seconds=10)
        assert format_time(td) == "10.000s"

    def test_milliseconds_only(self):
        """Test formatting with milliseconds only."""
        td = timedelta(milliseconds=500)
        assert format_time(td) == "500ms"

    def test_zero_duration(self):
        """Test formatting with zero duration."""
        td = timedelta()
        assert format_time(td) == "0ms"

    def test_small_milliseconds(self):
        """Test formatting with small milliseconds."""
        td = timedelta(milliseconds=5)
        assert format_time(td) == "5ms"

    def test_large_duration(self):
        """Test formatting with a large duration."""
        td = timedelta(hours=100, minutes=59, seconds=59)
        assert format_time(td) == "100h 59m 59s"
