# PlexMusicRatingsSync

[![PyPI Version](https://img.shields.io/pypi/v/PlexMusicRatingsSync)](https://pypi.org/project/PlexMusicRatingsSync/)
[![Python Version](https://img.shields.io/pypi/pyversions/PlexMusicRatingsSync)](https://pypi.org/project/PlexMusicRatingsSync/)
[![License](https://img.shields.io/github/license/rfgamaral/PlexMusicRatingsSync)](LICENSE)
[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue)](https://github.com/rfgamaral/PlexMusicRatingsSync/pkgs/container/plex-music-ratings-sync)

**Synchronize music ratings between Plex Media Server and your audio files.**

PlexMusicRatingsSync bridges the gap between Plex and your local audio files, ensuring your carefully curated music ratings stay consistent. Whether you rate songs in Plex or your favorite music player, this tool keeps everything in sync.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
  - [Using pipx (Recommended)](#using-pipx-recommended)
  - [Using pip](#using-pip)
  - [Using Docker](#using-docker)
- [Configuration](#configuration)
  - [Finding Your Plex Token](#finding-your-plex-token)
  - [Configuration File Locations](#configuration-file-locations)
- [Usage](#usage)
  - [Commands](#commands)
  - [Command Options](#command-options)
  - [Examples](#examples)
- [How It Works](#how-it-works)
  - [Sync Modes](#sync-modes)
  - [Supported Audio Formats](#supported-audio-formats)
  - [Rating Schemes](#rating-schemes)
- [Automation](#automation)
  - [Linux (Cron)](#linux-cron)
  - [macOS (launchd)](#macos-launchd)
  - [Windows (Task Scheduler)](#windows-task-scheduler)
  - [Docker (Ofelia)](#docker-ofelia)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Bidirectional Sync** - Synchronize ratings between Plex and audio files in both directions
- **One-Way Transfers** - Import ratings from files to Plex, or export from Plex to files
- **Half-Star Ratings** - Full support for 0.5-5.0 star ratings (1-10 scale internally)
- **Multiple Formats** - MP3, FLAC, M4A (AAC/ALAC), OGG, Opus, and AIFF
- **Multiple Libraries** - Sync across multiple Plex music libraries
- **Rating Scheme Compatibility** - Works with MusicBee, MediaMonkey, Picard, WMP, Winamp, foobar2000, and more
- **Dry-Run Mode** - Preview changes before applying them
- **Cross-Platform** - Works on Linux, macOS, and Windows
- **Docker Support** - Run in containers with easy scheduling

## Quick Start

**1. Install PlexMusicRatingsSync:**

```bash
pipx install PlexMusicRatingsSync
```

**2. Generate a configuration file:**

```bash
plex-music-ratings-sync info
```

**3. Edit the configuration file** (path shown in output) with your Plex server details:

```yaml
plex:
  url: http://localhost:32400
  token: YOUR_PLEX_TOKEN
  libraries:
    - Music
```

**4. Preview changes (dry-run):**

```bash
plex-music-ratings-sync sync --dry-run
```

**5. Run the sync:**

```bash
plex-music-ratings-sync sync
```

## Installation

### Using pipx (Recommended)

[pipx](https://github.com/pypa/pipx) installs Python applications in isolated environments, preventing dependency conflicts.

```bash
# Install pipx if you haven't already
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install PlexMusicRatingsSync
pipx install PlexMusicRatingsSync

# Upgrade to latest version
pipx upgrade PlexMusicRatingsSync

# Install a specific version
pipx install PlexMusicRatingsSync==2.0.0 --force
```

### Using pip

```bash
# Install globally (may require sudo on Linux/macOS)
pip install PlexMusicRatingsSync

# Or install in a virtual environment
python3 -m venv plex-sync-env
source plex-sync-env/bin/activate  # Linux/macOS
# plex-sync-env\Scripts\activate   # Windows
pip install PlexMusicRatingsSync
```

### Using Docker

Pull the image from GitHub Container Registry:

```bash
docker pull ghcr.io/rfgamaral/plex-music-ratings-sync
```

**Available tags:**

| Tag | Description |
|-----|-------------|
| `latest` | Most recent stable release |
| `2.0.0` | Specific version |
| `2.0` | Latest patch of version 2.0.x |
| `2` | Latest version 2.x.x |

## Configuration

### Finding Your Plex Token

1. Sign in to Plex Web App
2. Browse to any media item
3. Click the **...** (more options) button
4. Select **Get Info** > **View XML**
5. Look for `X-Plex-Token=` in the URL

Or follow the [official Plex guide](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).

### Configuration File Locations

The configuration file is created automatically when you run `plex-music-ratings-sync info`.

| Platform | Path |
|----------|------|
| **Linux** | `~/.config/PlexMusicRatingsSync/config.yml` |
| **macOS** | `~/Library/Application Support/PlexMusicRatingsSync/config.yml` |
| **Windows** | `%APPDATA%\PlexMusicRatingsSync\config.yml` |
| **Docker** | `/app/data/config.yml` (mount as volume) |

### Configuration Options

```yaml
plex:
  # Your Plex server URL
  # Use 'localhost' if running on the same machine as Plex
  url: http://localhost:32400

  # Your Plex authentication token (see "Finding Your Plex Token" above)
  token: xxxxxxxxxxxxxxxxxxxx

  # List of music library names to synchronize
  # Must match exactly as shown in Plex (case-sensitive)
  libraries:
    - Music
    - "Classical Music"
    - "My Vinyl Rips"
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `PMRS_CONFIG_DIR` | Override configuration directory |
| `PMRS_LOG_DIR` | Override log file directory |

## Usage

> **Important:** PlexMusicRatingsSync needs direct access to the same file paths that Plex uses. Run it on the same machine as your Plex server, or ensure paths match exactly via network shares or mapped drives.

### Commands

| Command | Description |
|---------|-------------|
| `info` | Display system information and config file location |
| `sync` | Bidirectional sync (Plex ↔ Files) |
| `import` | Import ratings from files → Plex |
| `export` | Export ratings from Plex → files |

**Alias:** You can use `pmrs` instead of `plex-music-ratings-sync`.

### Command Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview changes without applying them |
| `--quiet` | Suppress output except errors |
| `--verbose` | Show detailed debug information |
| `--version` | Show version and exit |
| `--help` | Show help message |

### Examples

```bash
# Show system info and config path
plex-music-ratings-sync info

# Preview what would change (recommended first run)
plex-music-ratings-sync sync --dry-run

# Sync ratings bidirectionally
plex-music-ratings-sync sync

# Import file ratings into Plex (verbose output)
plex-music-ratings-sync import --verbose

# Export Plex ratings to files (quiet mode for cron)
plex-music-ratings-sync export --quiet
```

**Docker examples:**

```bash
# Using docker run
docker run --rm \
  -v /path/to/config:/app/data \
  -v /path/to/music:/plex/music \
  ghcr.io/rfgamaral/plex-music-ratings-sync sync --dry-run

# Using docker compose
docker compose run --rm plex-music-ratings-sync sync
```

## How It Works

### Sync Modes

#### Bidirectional Sync (`sync`)

Synchronizes ratings in both directions. **Plex is the source of truth** when there's a conflict.

| Plex Rating | File Rating | Result |
|-------------|-------------|--------|
| 4 stars | 4 stars | No change |
| 4 stars | 3 stars | File updated to 4 stars |
| 4 stars | None | File updated to 4 stars |
| None | 3 stars | Plex updated to 3 stars |
| None | None | No change |

> **Why Plex wins conflicts:** Neither Plex nor audio files reliably store when a rating was last modified, so it's impossible to determine which rating is "newer."

#### Import (`import`)

One-way transfer: Files → Plex

- Only processes files that have a rating
- Updates Plex if different from file rating
- Skips files without ratings

#### Export (`export`)

One-way transfer: Plex → Files

- Only processes Plex tracks that have a rating
- Updates files if different from Plex rating
- Skips unrated Plex tracks

### Supported Audio Formats

| Format | Extension | Rating Storage |
|--------|-----------|----------------|
| MP3 | `.mp3` | ID3v2 POPM tag |
| FLAC | `.flac` | Vorbis Comments |
| M4A (AAC/ALAC) | `.m4a` | iTunes RATE atom |
| OGG Vorbis | `.ogg` | Vorbis Comments |
| Opus | `.opus` | Vorbis Comments |
| AIFF | `.aif`, `.aiff` | ID3v2 POPM tag |

### Rating Schemes

PlexMusicRatingsSync handles multiple rating schemes automatically:

| Application | Scale | Half-Star Support |
|-------------|-------|-------------------|
| **Plex** | 1-10 | Yes |
| **MusicBee** | 1-10 | Yes |
| **MediaMonkey** | 1-10 | Yes |
| **Windows Media Player** | 1-5 | No |
| **Winamp** | 1-5 | No |
| **foobar2000** | 1-5 | No |
| **Picard** | 1-5 | No |

**How it works:**

- When **reading** MP3 files, the tool checks for Plex's rating scheme first, then falls back to other schemes
- When **writing** MP3 files, ratings are stored using the primary POPM format for maximum compatibility
- FLAC, OGG, and Opus use a 10-100 scale in Vorbis Comments (10 × Plex rating)
- M4A files use iTunes' 10-100 scale

## Automation

### Linux (Cron)

```bash
# Edit crontab
crontab -e

# Add a scheduled job (examples):

# Daily at 3:00 AM
0 3 * * * /home/user/.local/bin/plex-music-ratings-sync sync --quiet

# Every Sunday at 3:00 AM
0 3 * * 0 /home/user/.local/bin/plex-music-ratings-sync sync --quiet

# Every 6 hours
0 */6 * * * /home/user/.local/bin/plex-music-ratings-sync sync --quiet
```

> **Note:** Use `which plex-music-ratings-sync` to find the correct executable path on your system.

### macOS (launchd)

Create `~/Library/LaunchAgents/com.plexmusicratings.sync.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.plexmusicratings.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/plex-music-ratings-sync</string>
        <string>sync</string>
        <string>--quiet</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>3</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

Load the agent:

```bash
launchctl load ~/Library/LaunchAgents/com.plexmusicratings.sync.plist
```

### Windows (Task Scheduler)

1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. Set name: "PlexMusicRatingsSync"
4. Choose trigger: **Daily** (or your preference)
5. Action: **Start a program**
6. Program: `%USERPROFILE%\.local\bin\plex-music-ratings-sync.exe`
7. Arguments: `sync --quiet`
8. Finish and optionally configure additional settings

### Docker (Ofelia)

Use [Ofelia](https://github.com/mcuadros/ofelia) for Docker-native job scheduling.

Create `docker-compose.yml`:

```yaml
services:
  plex-music-ratings-sync:
    image: ghcr.io/rfgamaral/plex-music-ratings-sync
    container_name: plex-music-ratings-sync
    network_mode: bridge
    command: sync
    restart: on-failure:2
    volumes:
      - /path/to/config:/app/data         # Your config directory
      - /path/to/music:/plex/music        # Must match Plex's path!

  ofelia-scheduler:
    image: mcuadros/ofelia
    container_name: ofelia-scheduler
    command: daemon --docker
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    labels:
      ofelia.job-run.plex-music-ratings-sync.schedule: "@every 6h"
      ofelia.job-run.plex-music-ratings-sync.container: "plex-music-ratings-sync"
```

Start the scheduler:

```bash
# Create containers without starting them
docker compose up --no-start

# Start only the scheduler (runs sync every 6 hours)
docker compose up -d ofelia-scheduler
```

> **Note:** Using `docker compose up` without `--no-start` will trigger an immediate sync before the scheduler takes over.

## Troubleshooting

### Common Issues

#### "File not found" errors

**Cause:** The tool can't access the audio files at the paths Plex reports.

**Solution:** Ensure you're running on the same machine as Plex, or that paths match exactly via network shares. Verify the correct path by opening a track in Plex → **...** → **Get Info** and checking the file path.

#### "Library not found" errors

**Cause:** The library name in your config doesn't match Plex exactly.

**Solution:** Library names are case-sensitive. Copy the exact name from Plex's sidebar.

#### No ratings are synced

**Cause:** Files might be in an unsupported format, or paths don't match.

**Solution:**
1. Run with `--verbose` to see detailed output
2. Check that your files are in a supported format
3. Verify file paths match between Plex and your filesystem

#### "Another instance is already running"

**Cause:** A previous run didn't complete cleanly, or another instance is actually running.

**Solution:** Wait for the other process to finish, or delete the lock file:
- Linux/macOS: `~/.cache/PlexMusicRatingsSync/process.lock`
- Windows: `%LOCALAPPDATA%\PlexMusicRatingsSync\Cache\process.lock`

#### Docker volume path issues

**Cause:** Container paths don't match what Plex sees.

**Solution:** The right side of your music volume mount must exactly match Plex's internal path. If Plex shows `/plex/music/Artist/Album/track.mp3`, your volume must be `-v /host/path:/plex/music`.

### Log Files

Log files are stored at:

| Platform | Path |
|----------|------|
| **Linux** | `~/.local/state/PlexMusicRatingsSync/logs/` |
| **macOS** | `~/Library/Logs/PlexMusicRatingsSync/` |
| **Windows** | `%LOCALAPPDATA%\PlexMusicRatingsSync\Logs\` |
| **Docker** | `/app/data/logs/` (if using default config) |

## FAQ

### How do I ensure file paths match between Plex and PlexMusicRatingsSync?

Open any track in Plex, click **...** → **Get Info**, and note the file path. This exact path must be accessible when you run the tool. For Docker, this path must match your container's volume mount.

### Why does Plex always win when ratings conflict?

Neither Plex nor audio file metadata reliably stores "last modified" timestamps for ratings. Without this information, we can't determine which rating is newer, so Plex is used as the authoritative source for consistency.

### Can I sync ratings from my music player to Plex?

Yes! Use the `import` command to copy ratings from your audio files (tagged by your music player) into Plex:

```bash
plex-music-ratings-sync import
```

### Do half-star ratings work?

Yes, with compatible applications. Plex and applications using the "primary POPM" scheme (MusicBee, MediaMonkey) support half-star ratings (e.g., 3.5 stars). Applications using the "alternative POPM" scheme (WMP, Winamp, foobar2000) only support full-star ratings.

### What happens to unsupported file formats?

Files in unsupported formats (e.g., WMA, WAV) are skipped with a warning. No changes are made to them.

### Can I use this with multiple Plex libraries?

Yes! List all your music libraries in the config file:

```yaml
plex:
  libraries:
    - Music
    - Classical
    - Audiobooks
```

### Is my Plex token secure?

Your token is stored locally in your config file. Never share your config file or commit it to version control. Consider using restrictive file permissions (`chmod 600 config.yml` on Linux/macOS).

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests on [GitHub](https://github.com/rfgamaral/PlexMusicRatingsSync).

### Development Setup

```bash
# Clone the repository
git clone https://github.com/rfgamaral/PlexMusicRatingsSync.git
cd PlexMusicRatingsSync

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Run the tool
plex-music-ratings-sync --help
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with care for music lovers who appreciate well-organized libraries.**
