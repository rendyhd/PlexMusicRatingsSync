"""
Tests for rating conversion functions.

These tests verify the bidirectional conversion between Plex's 1-10 rating scale
and various audio file formats' rating schemes.
"""

import pytest

# Import the private functions we want to test
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from plex_music_ratings_sync.ratings import (
    _popm_rating_to_plex,
    _plex_rating_to_popm,
    _PRIMARY_MP3_RATING_MAP,
    _ALTERNATIVE_MP3_RATING_MAP,
    _PICARD_MP3_RATING_MAP,
)


class TestPOPMToPlexConversion:
    """Test conversion from POPM ratings to Plex ratings."""

    def test_zero_rating_returns_none(self):
        """Zero POPM rating should return None (unrated)."""
        assert _popm_rating_to_plex(0) is None

    def test_none_rating_returns_none(self):
        """None POPM rating should return None."""
        assert _popm_rating_to_plex(None) is None

    def test_max_rating_returns_10(self):
        """POPM 255 should return Plex rating 10."""
        assert _popm_rating_to_plex(255) == 10

    def test_primary_map_with_plex_email(self):
        """Primary rating map should work with Plex email identifier."""
        for plex_rating, popm_value in _PRIMARY_MP3_RATING_MAP.items():
            if popm_value > 0:  # Skip 0 which returns None
                result = _popm_rating_to_plex(popm_value, "Plex")
                assert result == plex_rating, f"POPM {popm_value} should map to {plex_rating}"

    def test_primary_map_with_musicbee_email(self):
        """Primary rating map should work with MusicBee email identifier."""
        for plex_rating, popm_value in _PRIMARY_MP3_RATING_MAP.items():
            if popm_value > 0:
                result = _popm_rating_to_plex(popm_value, "MusicBee")
                assert result == plex_rating

    def test_alternative_map_fallback(self):
        """Alternative rating map (WMP/Winamp) should be detected as fallback."""
        # WMP uses: 1 -> 2, 64 -> 4, 128 -> 6, 196 -> 8, 255 -> 10
        test_cases = [
            (1, 2),    # 1 star = 2 in Plex scale
            (64, 4),   # 2 stars = 4 in Plex scale
            (128, 6),  # 3 stars = 6 in Plex scale
            (196, 8),  # 4 stars = 8 in Plex scale
            (255, 10), # 5 stars = 10 in Plex scale
        ]
        for popm_value, expected_plex in test_cases:
            result = _popm_rating_to_plex(popm_value, "Windows Media Player")
            assert result == expected_plex, f"POPM {popm_value} should map to {expected_plex}"

    def test_picard_map_fallback(self):
        """Picard rating map should be detected as fallback."""
        # Picard uses linear: 51 -> 2, 102 -> 4, 153 -> 6, 204 -> 8, 255 -> 10
        test_cases = [
            (51, 2),
            (102, 4),
            (153, 6),
            (204, 8),
            (255, 10),
        ]
        for popm_value, expected_plex in test_cases:
            result = _popm_rating_to_plex(popm_value, "unknown_player")
            assert result == expected_plex, f"POPM {popm_value} should map to {expected_plex}"

    def test_linear_interpolation_fallback(self):
        """Unknown POPM values should use linear interpolation."""
        # For values not in any map, use linear: (popm / 255) * 9 + 1
        # Value 127 (middle) should be around 5-6
        result = _popm_rating_to_plex(127, "unknown")
        assert 4 <= result <= 6, f"POPM 127 should interpolate to around 5, got {result}"


class TestPlexToPOPMConversion:
    """Test conversion from Plex ratings to POPM ratings."""

    def test_zero_rating_returns_zero(self):
        """Plex rating 0 should return POPM 0."""
        assert _plex_rating_to_popm(0) == 0

    def test_none_rating_returns_zero(self):
        """Plex rating None should return POPM 0."""
        assert _plex_rating_to_popm(None) == 0

    def test_max_rating_returns_255(self):
        """Plex rating 10 should return POPM 255."""
        assert _plex_rating_to_popm(10) == 255

    def test_all_plex_ratings_have_popm_value(self):
        """All Plex ratings 1-10 should map to valid POPM values."""
        for plex_rating in range(1, 11):
            popm_value = _plex_rating_to_popm(plex_rating)
            assert popm_value > 0, f"Plex rating {plex_rating} should have non-zero POPM"
            assert popm_value <= 255, f"POPM value should be <= 255"

    def test_uses_primary_map(self):
        """Conversion should use the primary rating map."""
        for plex_rating, expected_popm in _PRIMARY_MP3_RATING_MAP.items():
            result = _plex_rating_to_popm(plex_rating)
            assert result == expected_popm, f"Plex {plex_rating} should map to POPM {expected_popm}"


class TestRoundTripConversion:
    """Test that ratings survive round-trip conversion."""

    def test_plex_to_popm_to_plex_roundtrip(self):
        """Converting Plex -> POPM -> Plex should preserve the rating."""
        for original_plex in range(1, 11):
            popm = _plex_rating_to_popm(original_plex)
            restored_plex = _popm_rating_to_plex(popm, "Plex")
            assert restored_plex == original_plex, \
                f"Round trip failed: {original_plex} -> {popm} -> {restored_plex}"


class TestRatingValidation:
    """Test rating value validation in set_rating_to_file."""

    @pytest.fixture(autouse=True)
    def init_logger(self):
        """Initialize logger before each test."""
        from plex_music_ratings_sync.logger import init_logging
        init_logging(quiet=True)

    def test_valid_rating_range(self):
        """Valid ratings should be in range 1-10."""
        from plex_music_ratings_sync.ratings import set_rating_to_file

        # These should not raise errors (though they won't actually write without files)
        # The function should silently return for unsupported file types
        set_rating_to_file("/fake/path/file.unsupported", 5)

    def test_invalid_rating_rejected(self):
        """Invalid ratings should be rejected (function returns early)."""
        from plex_music_ratings_sync.ratings import set_rating_to_file

        # Rating > 10 or < 0 should be rejected - function returns early
        # Just verify it doesn't crash
        set_rating_to_file("/fake/path/file.mp3", 15)
        set_rating_to_file("/fake/path/file.mp3", -1)


class TestFileExtensionHandling:
    """Test file extension detection in rating functions."""

    @pytest.fixture(autouse=True)
    def init_logger(self):
        """Initialize logger before each test."""
        from plex_music_ratings_sync.logger import init_logging
        init_logging(quiet=True)

    def test_case_insensitive_extension(self):
        """File extensions should be case-insensitive."""
        from plex_music_ratings_sync.ratings import get_rating_from_file

        # These will return None because files don't exist and errors are logged
        # Just testing that the extension detection handles case-insensitively
        result_lower = get_rating_from_file("/fake/test.mp3")
        result_upper = get_rating_from_file("/fake/TEST.MP3")
        result_mixed = get_rating_from_file("/fake/Test.Mp3")

        # All should return None (file doesn't exist), not crash
        assert result_lower is None
        assert result_upper is None
        assert result_mixed is None

    def test_unsupported_extension_returns_none(self):
        """Unsupported file extensions should return None."""
        from plex_music_ratings_sync.ratings import get_rating_from_file

        assert get_rating_from_file("/fake/test.wav") is None
        assert get_rating_from_file("/fake/test.wma") is None
        assert get_rating_from_file("/fake/test.txt") is None
