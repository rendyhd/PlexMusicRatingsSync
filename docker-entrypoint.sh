#!/bin/sh
set -e

# If PMRS_SCHEDULE is set, run in scheduled mode
if [ -n "$PMRS_SCHEDULE" ]; then
    echo "PlexMusicRatingsSync - Scheduled Mode"
    echo "Schedule: $PMRS_SCHEDULE"
    echo "Command: $PMRS_COMMAND $PMRS_ARGS"
    echo "---"

    # Create crontab file
    echo "$PMRS_SCHEDULE /usr/local/bin/plex-music-ratings-sync $PMRS_COMMAND $PMRS_ARGS" > /tmp/crontab

    # Run supercronic (stays in foreground)
    exec /usr/local/bin/supercronic /tmp/crontab
else
    # One-shot mode: run the command and exit
    # If arguments provided, use them; otherwise use defaults
    if [ $# -gt 0 ]; then
        exec /usr/local/bin/plex-music-ratings-sync "$@"
    elif [ -n "$PMRS_COMMAND" ]; then
        # shellcheck disable=SC2086
        exec /usr/local/bin/plex-music-ratings-sync $PMRS_COMMAND $PMRS_ARGS
    else
        exec /usr/local/bin/plex-music-ratings-sync --help
    fi
fi
