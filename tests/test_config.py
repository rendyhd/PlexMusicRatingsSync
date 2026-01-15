"""
Tests for configuration loading and validation.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestConfigValidation:
    """Test configuration validation."""

    @pytest.fixture(autouse=True)
    def init_logger(self):
        """Initialize logger before each test."""
        from plex_music_ratings_sync.logger import init_logging
        init_logging(quiet=True)

    def test_valid_config_accepted(self, temp_dir, monkeypatch):
        """A valid configuration should be accepted."""
        # Create a valid config file
        config_path = temp_dir / "config.yml"
        config_data = {
            "plex": {
                "url": "http://localhost:32400",
                "token": "valid_token_123",
                "libraries": ["Music"],
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Set environment to use our temp directory
        monkeypatch.setenv("PMRS_CONFIG_DIR", str(temp_dir))

        # Reset the global config state
        import plex_music_ratings_sync.config as config_module
        config_module._config = None

        # This should not raise
        config_module.init_config()
        result = config_module.get_plex_config()

        assert result["url"] == "http://localhost:32400"
        assert result["token"] == "valid_token_123"
        assert result["libraries"] == ["Music"]

    def test_missing_url_rejected(self, temp_dir, monkeypatch):
        """Configuration without URL should be rejected."""
        config_path = temp_dir / "config.yml"
        config_data = {
            "plex": {
                "token": "valid_token",
                "libraries": ["Music"],
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        monkeypatch.setenv("PMRS_CONFIG_DIR", str(temp_dir))

        import plex_music_ratings_sync.config as config_module
        config_module._config = None

        config_module.init_config()

        with pytest.raises(SystemExit):
            config_module.get_plex_config()

    def test_missing_token_rejected(self, temp_dir, monkeypatch):
        """Configuration without token should be rejected."""
        config_path = temp_dir / "config.yml"
        config_data = {
            "plex": {
                "url": "http://localhost:32400",
                "libraries": ["Music"],
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        monkeypatch.setenv("PMRS_CONFIG_DIR", str(temp_dir))

        import plex_music_ratings_sync.config as config_module
        config_module._config = None

        config_module.init_config()

        with pytest.raises(SystemExit):
            config_module.get_plex_config()

    def test_empty_libraries_rejected(self, temp_dir, monkeypatch):
        """Configuration with empty libraries list should be rejected."""
        config_path = temp_dir / "config.yml"
        config_data = {
            "plex": {
                "url": "http://localhost:32400",
                "token": "valid_token",
                "libraries": [],
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        monkeypatch.setenv("PMRS_CONFIG_DIR", str(temp_dir))

        import plex_music_ratings_sync.config as config_module
        config_module._config = None

        config_module.init_config()

        with pytest.raises(SystemExit):
            config_module.get_plex_config()

    def test_invalid_url_scheme_rejected(self, temp_dir, monkeypatch):
        """URL without http/https should be rejected."""
        config_path = temp_dir / "config.yml"
        config_data = {
            "plex": {
                "url": "ftp://localhost:32400",
                "token": "valid_token",
                "libraries": ["Music"],
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        monkeypatch.setenv("PMRS_CONFIG_DIR", str(temp_dir))

        import plex_music_ratings_sync.config as config_module
        config_module._config = None

        config_module.init_config()

        with pytest.raises(SystemExit):
            config_module.get_plex_config()

    def test_https_url_accepted(self, temp_dir, monkeypatch):
        """HTTPS URLs should be accepted."""
        config_path = temp_dir / "config.yml"
        config_data = {
            "plex": {
                "url": "https://plex.example.com:32400",
                "token": "valid_token",
                "libraries": ["Music"],
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        monkeypatch.setenv("PMRS_CONFIG_DIR", str(temp_dir))

        import plex_music_ratings_sync.config as config_module
        config_module._config = None

        config_module.init_config()
        result = config_module.get_plex_config()

        assert result["url"] == "https://plex.example.com:32400"

    def test_whitespace_stripped(self, temp_dir, monkeypatch):
        """Whitespace in URL and token should be stripped."""
        config_path = temp_dir / "config.yml"
        config_data = {
            "plex": {
                "url": "  http://localhost:32400  ",
                "token": "  token_with_spaces  ",
                "libraries": ["Music"],
            }
        }
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        monkeypatch.setenv("PMRS_CONFIG_DIR", str(temp_dir))

        import plex_music_ratings_sync.config as config_module
        config_module._config = None

        config_module.init_config()
        result = config_module.get_plex_config()

        assert result["url"] == "http://localhost:32400"
        assert result["token"] == "token_with_spaces"

    def test_empty_config_file_rejected(self, temp_dir, monkeypatch):
        """Empty config file should be rejected."""
        config_path = temp_dir / "config.yml"
        config_path.touch()  # Create empty file

        monkeypatch.setenv("PMRS_CONFIG_DIR", str(temp_dir))

        import plex_music_ratings_sync.config as config_module
        config_module._config = None

        with pytest.raises(SystemExit):
            config_module.init_config()

    def test_invalid_yaml_rejected(self, temp_dir, monkeypatch):
        """Invalid YAML syntax should be rejected."""
        config_path = temp_dir / "config.yml"
        with open(config_path, "w") as f:
            f.write("plex:\n  url: [invalid yaml\n")

        monkeypatch.setenv("PMRS_CONFIG_DIR", str(temp_dir))

        import plex_music_ratings_sync.config as config_module
        config_module._config = None

        with pytest.raises(SystemExit):
            config_module.init_config()


class TestConfigFileCreation:
    """Test configuration file creation from template."""

    @pytest.fixture(autouse=True)
    def init_logger(self):
        """Initialize logger before each test."""
        from plex_music_ratings_sync.logger import init_logging
        init_logging(quiet=True)

    def test_config_created_from_template(self, temp_dir, monkeypatch):
        """Config file should be created from template if it doesn't exist."""
        monkeypatch.setenv("PMRS_CONFIG_DIR", str(temp_dir))

        import plex_music_ratings_sync.config as config_module
        config_module._config = None

        # The init should create a config file from template
        # (will fail on get_plex_config since template has placeholders)
        config_module.init_config()

        config_path = temp_dir / "config.yml"
        assert config_path.exists(), "Config file should be created"
