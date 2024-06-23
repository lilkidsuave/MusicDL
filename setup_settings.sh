#!/bin/bash

# Ensure required environment variables are set
if [[ -z "$QOBUZ_USERNAME" ]]; then
    echo "Error: QOBUZ_USERNAME environment variable not set"
    exit 1
fi

if [[ -z "$QOBUZ_PASSWORD" ]]; then
    echo "Error: QOBUZ_PASSWORD environment variable not set"
    exit 1
fi

# Create or edit settings.json in the config directory
echo '{
  "global": {
    "general": {
      "download_path": "./downloads/",
      "download_quality": "hifi",
      "search_limit": 10
    },
    "module_defaults": {
      "lyrics": "default",
      "covers": "default",
      "credits": "default"
    }
  },
  "extensions": {},
  "modules": {
    "qobuz": {
      "app_id": "950096963",
      "app_secret": "979549437fcc4a3faad4867b5cd25dcb",
      "quality_format": "{sample_rate}kHz {bit_depth}bit",
      "username": "'"$QOBUZ_USERNAME"'",
      "password": "'"$QOBUZ_PASSWORD"'"
    }
  }
}' > /app/config/settings.json

# Run the main application command
exec "$@"
