"""
Pytest configuration and fixtures for PlexMusicRatingsSync tests.
"""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config():
    """Return a sample valid configuration dictionary."""
    return {
        "plex": {
            "url": "http://localhost:32400",
            "token": "test_token_12345",
            "libraries": ["Music", "Classical"],
        }
    }


@pytest.fixture
def sample_config_file(temp_dir, sample_config):
    """Create a sample config file and return its path."""
    import yaml

    config_path = temp_dir / "config.yml"
    with open(config_path, "w") as f:
        yaml.dump(sample_config, f)
    return config_path


@pytest.fixture
def mock_env_config_dir(temp_dir, monkeypatch):
    """Set environment variable for config directory."""
    monkeypatch.setenv("PMRS_CONFIG_DIR", str(temp_dir))
    return temp_dir


@pytest.fixture
def mock_env_log_dir(temp_dir, monkeypatch):
    """Set environment variable for log directory."""
    monkeypatch.setenv("PMRS_LOG_DIR", str(temp_dir))
    return temp_dir
