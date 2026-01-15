import os
import sys
from shutil import copyfile

import yaml

from plex_music_ratings_sync.logger import log_error, log_warning
from plex_music_ratings_sync.util.paths import (
    get_config_dir,
    get_config_file_path,
    get_template_file_path,
)

_config = None
"""User configuration data."""


def _create_config(config_file_path):
    """
    Create a new configuration file from the template.

    Args:
        config_file_path: Path where the config file should be created

    Raises:
        SystemExit: If template file is missing or config creation fails
    """
    template_path = get_template_file_path()

    try:
        copyfile(template_path, config_file_path)

        # Set restrictive permissions (owner read/write only) for security
        # The config file contains the Plex authentication token
        try:
            os.chmod(config_file_path, 0o600)
        except OSError:
            # On Windows, chmod may not work as expected, but that's OK
            pass

    except FileNotFoundError:
        log_error(f"Template config file not found: **{template_path}**")
        sys.exit(1)
    except (IOError, OSError) as e:
        log_error(f"Failed to create config file: {e}")
        sys.exit(1)


def init_config():
    """
    Initialize the configuration by loading and parsing the YAML config file.

    Creates the config directory and file if they don't exist.
    Validates that the config file contains valid YAML.

    Raises:
        SystemExit: If config file is invalid or cannot be read
    """
    global _config

    config_dir = get_config_dir()

    if not config_dir.exists():
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            log_error(f"Failed to create config directory: {e}")
            sys.exit(1)

    config_file_path = get_config_file_path()

    if not config_file_path.exists():
        _create_config(config_file_path)

    try:
        with open(config_file_path, "r") as config_file:
            content = config_file.read()

        if not content.strip():
            log_error(
                f"Config file is empty. Please edit: **{config_file_path}**"
            )
            sys.exit(1)

        _config = yaml.safe_load(content)

        if _config is None:
            log_error(
                f"Config file contains no valid YAML content. Please edit: **{config_file_path}**"
            )
            sys.exit(1)

        if not isinstance(_config, dict):
            log_error("Config file must contain a YAML dictionary/mapping")
            sys.exit(1)

    except yaml.YAMLError as e:
        log_error(f"Failed to parse config file (invalid YAML syntax): {e}")
        sys.exit(1)
    except IOError as e:
        log_error(f"Failed to read config file: {e}")
        sys.exit(1)


def get_plex_config():
    """
    Retrieve and validate the Plex configuration.

    Returns:
        dict: Validated Plex configuration with url, token, and libraries

    Raises:
        SystemExit: If configuration is missing or invalid
    """
    if _config is None:
        log_error("Configuration not initialized. Call init_config() first.")
        sys.exit(1)

    if "plex" not in _config:
        log_error("Missing 'plex' section in config file")
        sys.exit(1)

    plex_config = _config.get("plex", {})

    # Validate URL
    plex_url = plex_config.get("url")
    if not isinstance(plex_url, str) or not plex_url.strip():
        log_error("Plex URL is missing or empty in config file")
        sys.exit(1)

    plex_url = plex_url.strip()
    if not (plex_url.startswith("http://") or plex_url.startswith("https://")):
        log_error("Plex URL must start with http:// or https://")
        sys.exit(1)

    # Validate token
    plex_token = plex_config.get("token")
    if not isinstance(plex_token, str) or not plex_token.strip():
        log_error("Plex token is missing or empty in config file")
        sys.exit(1)

    # Validate libraries
    libraries = plex_config.get("libraries")
    if not isinstance(libraries, list):
        log_error("'libraries' must be a list in config file")
        sys.exit(1)

    if not libraries:
        log_error("'libraries' list cannot be empty in config file")
        sys.exit(1)

    # Filter out any empty library names
    valid_libraries = [lib for lib in libraries if isinstance(lib, str) and lib.strip()]
    if not valid_libraries:
        log_error("'libraries' must contain at least one valid library name")
        sys.exit(1)

    # Warn about config file permissions (security reminder)
    config_file_path = get_config_file_path()
    try:
        file_mode = os.stat(config_file_path).st_mode & 0o777
        if file_mode & 0o077:  # Check if group/others have any permissions
            log_warning(
                "Config file contains sensitive credentials. "
                "Consider restricting permissions: chmod 600 config.yml"
            )
    except OSError:
        pass  # Skip permission check on platforms where it's not supported

    return {
        "url": plex_url.strip(),
        "token": plex_token.strip(),
        "libraries": valid_libraries,
    }
