import atexit
import sys
from pathlib import Path

from filelock import FileLock, Timeout
from platformdirs import user_cache_dir

from plex_music_ratings_sync import APP_NAME

_process_lock_file = Path(user_cache_dir(APP_NAME)) / "process.lock"
"""Path to the single process lock file."""

_process_lock_file.parent.mkdir(parents=True, exist_ok=True)

_process_lock = FileLock(_process_lock_file)
"""File lock to ensure only one instance of the application is running."""


def _cleanup_lock():
    """Release the lock and remove the lock file."""
    try:
        if _process_lock.is_locked:
            _process_lock.release()

        if _process_lock_file.exists():
            _process_lock_file.unlink()
    except OSError as e:
        # Import here to avoid circular import during module initialization
        try:
            from plex_music_ratings_sync.logger import log_warning
            log_warning(f"Failed to cleanup process lock: {e}")
        except ImportError:
            pass  # Logger not available, skip warning


def acquire_process_lock():
    """
    Try to acquire the process lock. Exit if already locked.

    This prevents multiple instances of the application from running
    simultaneously, which could cause data corruption.

    Raises:
        SystemExit: If another instance is already running
    """
    try:
        _process_lock.acquire(timeout=0.1)

        atexit.register(_cleanup_lock)
    except Timeout:
        # Import here to avoid circular import during module initialization
        try:
            from plex_music_ratings_sync.logger import log_error
            log_error(f"Another instance of {APP_NAME} is already running. Exiting.")
        except ImportError:
            # Fallback to print if logger is not available
            print(f"Another instance of {APP_NAME} is already running. Exiting.")
        sys.exit(1)
