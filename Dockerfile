# Build stage
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Download supercronic for built-in scheduling
ARG TARGETARCH
RUN case "${TARGETARCH}" in \
        "amd64") ARCH="linux-amd64" ;; \
        "arm64") ARCH="linux-arm64" ;; \
        "arm") ARCH="linux-arm" ;; \
        *) ARCH="linux-amd64" ;; \
    esac && \
    wget -q "https://github.com/aptible/supercronic/releases/download/v0.2.29/supercronic-${ARCH}" \
        -O /usr/local/bin/supercronic && \
    chmod +x /usr/local/bin/supercronic

# Runtime stage
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash pmrs

WORKDIR /app

# Environment variables
ENV PMRS_CONFIG_DIR=/app/data \
    PMRS_LOG_DIR=/app/data \
    FORCE_COLOR=1 \
    PYTHONUNBUFFERED=1 \
    # Schedule configuration (empty = run once and exit)
    # Examples: "0 3 * * *" (daily at 3am), "@hourly", "@daily"
    PMRS_SCHEDULE="" \
    # Default command to run (sync, import, export)
    PMRS_COMMAND="sync" \
    # Additional arguments (e.g., "--quiet", "--verbose", "--dry-run")
    PMRS_ARGS=""

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy supercronic from builder
COPY --from=builder /usr/local/bin/supercronic /usr/local/bin/supercronic

# Copy application code
COPY src/plex_music_ratings_sync /app/plex_music_ratings_sync

# Create CLI wrapper scripts
RUN echo '#!/bin/sh\nexec python -u -m plex_music_ratings_sync "$@"' > /usr/local/bin/plex-music-ratings-sync && \
    chmod +x /usr/local/bin/plex-music-ratings-sync && \
    ln -s /usr/local/bin/plex-music-ratings-sync /usr/local/bin/pmrs

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create data directory and set permissions
RUN mkdir -p /app/data && chown -R pmrs:pmrs /app /app/data

# Declare volume for config and logs
VOLUME ["/app/data"]

# Switch to non-root user
USER pmrs

# Health check - verifies Python and the module are accessible
HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import plex_music_ratings_sync; print('OK')" || exit 1

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Default command (shows help if no arguments and no schedule)
CMD []
