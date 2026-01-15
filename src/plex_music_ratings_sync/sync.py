import sys
from datetime import datetime
from pathlib import Path

from plexapi.exceptions import BadRequest, NotFound, Unauthorized
from plexapi.server import PlexServer
from requests.exceptions import ConnectionError, Timeout

from plex_music_ratings_sync.config import get_plex_config
from plex_music_ratings_sync.logger import log_debug, log_error, log_info, log_warning
from plex_music_ratings_sync.ratings import (
    get_rating_from_file,
    get_rating_from_plex,
    set_rating_to_file,
    set_rating_to_plex,
)
from plex_music_ratings_sync.state import is_dry_run
from plex_music_ratings_sync.util.datetime import format_time

_SUPPORTED_EXTENSIONS = (".flac", ".m4a", ".mp3", ".ogg", ".opus", ".aif", ".aiff")
"""Audio file extensions that are supported for rating synchronization."""


def _get_track_file_path(track):
    """
    Safely extract the file path from a Plex track item.

    Args:
        track: A Plex track object

    Returns:
        Path object if successful, None if track has no media/parts
    """
    try:
        if not track.media:
            return None
        if not track.media[0].parts:
            return None
        return Path(track.media[0].parts[0].file)
    except (AttributeError, IndexError, TypeError):
        return None


class RatingSync:
    def __init__(self):
        plex_config = get_plex_config()
        plex_url = plex_config["url"]
        plex_token = plex_config["token"]

        try:
            log_info(f"Connecting to Plex server: **{plex_url}**")
            self.plex = PlexServer(plex_url, plex_token)
            log_info(f"Connected to Plex server: **{self.plex.friendlyName}**")
        except Unauthorized:
            log_error("Failed to connect to Plex server: Invalid or expired token")
            sys.exit(1)
        except (ConnectionError, Timeout) as e:
            log_error(f"Failed to connect to Plex server: Connection error - {e}")
            sys.exit(1)
        except BadRequest as e:
            log_error(f"Failed to connect to Plex server: Bad request - {e}")
            sys.exit(1)
        except Exception as e:
            # Sanitize error message to prevent token exposure
            error_msg = str(e)
            if plex_token in error_msg:
                error_msg = error_msg.replace(plex_token, "***REDACTED***")
            log_error(f"Failed to connect to Plex server: {error_msg}")
            sys.exit(1)

        self.libraries = plex_config["libraries"]

        if is_dry_run():
            log_warning("Running in dry-run mode (no changes will be made)")

    def _process_item(self, item, mode="sync"):
        """
        Process a single track with the specified mode:
        - `sync`: Bidirectional sync between Plex and files
        - `import`: One-way import from audio files to Plex
        - `export`: One-way export from Plex to audio files
        """
        item_start_time = datetime.now()

        file_path = _get_track_file_path(item)
        if file_path is None:
            log_warning(f"▸ Track has no media file information: **{item.title}**", 4)
            return

        track_index = item.index if item.index is not None else 0

        log_info(
            f"Track: **{track_index:02d}. {item.title}** __({file_path.name})__",
            3,
        )

        if not file_path.exists():
            log_warning("▸ File not found on disk", 4)
            return

        if file_path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            log_warning("▸ Skipping unsupported file type", 4)
            return

        plex_rating = get_rating_from_plex(item)
        file_rating = get_rating_from_file(str(file_path))

        if mode == "import" and file_rating is not None:
            if plex_rating != file_rating:
                set_rating_to_plex(item, file_rating)
            else:
                log_debug("▸ Plex rating already matches file", 4)
        elif mode == "export" and plex_rating is not None:
            if file_rating != plex_rating:
                set_rating_to_file(str(file_path), plex_rating)
            else:
                log_debug("▸ File rating already matches Plex", 4)
        elif mode == "sync":
            if plex_rating != file_rating:
                if plex_rating is not None:
                    set_rating_to_file(str(file_path), plex_rating)
                elif file_rating is not None:
                    set_rating_to_plex(item, file_rating)
            else:
                log_debug("▸ Ratings are already in sync", 4)

        item_elapsed_time = datetime.now() - item_start_time

        log_debug(f"▸ Processed in **{format_time(item_elapsed_time)}**", 4)

    def _process_libraries(self, mode="sync"):
        """Process all configured libraries with the specified mode."""
        total_start_time = datetime.now()
        processed_tracks = 0

        for library_name in self.libraries:
            log_info(f"Processing Plex library: **{library_name}**")

            music_items = self.plex.library.section(library_name).all()

            if not music_items:
                log_warning(f"No items found in library: **{library_name}**")
                continue

            for item in music_items:
                if hasattr(item, "type") and item.type == "artist":
                    log_info(f"Artist: **{item.title}**", 1)

                    for album in item.albums():
                        album_tracks = album.tracks()

                        # Skip albums with no tracks
                        if not album_tracks:
                            log_warning(f"Album has no tracks: **{album.title}**", 2)
                            continue

                        # Get album path from first track with valid media
                        album_path = None
                        for track in album_tracks:
                            track_path = _get_track_file_path(track)
                            if track_path:
                                album_path = track_path.parent
                                break

                        if album_path is None:
                            log_warning(
                                f"Album: **{album.title}** __(could not determine path)__",
                                2,
                            )
                        else:
                            log_info(
                                f"Album: **{album.title}** __({album_path})__",
                                2,
                            )

                        for track in album_tracks:
                            self._process_item(track, mode=mode)
                            processed_tracks += 1

        total_elapsed_item = datetime.now() - total_start_time

        log_info(
            f"Processed **{processed_tracks}** tracks in **{format_time(total_elapsed_item)}**"
        )

    def sync_ratings(self):
        """Synchronize ratings between Plex and supported audio files."""
        log_info("Synchronization started: **Plex ⇄ Audio Files**")

        self._process_libraries(mode="sync")

        log_info("Synchronization completed: **Plex** ⇄ **Audio Files**")

    def import_ratings(self):
        """Import ratings from audio files into Plex."""
        log_info("Import started: **Audio Files → Plex**")

        self._process_libraries(mode="import")

        log_info("Import completed: **Audio Files → Plex**")

    def export_ratings(self):
        """Export ratings from Plex to audio files."""
        log_info("Export started: **Plex → Audio Files**")

        self._process_libraries(mode="export")

        log_info("Export completed: **Plex → Audio Files**")
