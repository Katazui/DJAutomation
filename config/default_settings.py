"""
default_settings.py

Default configuration for DJ Automation.
This file serves as a template for user-specific settings.
Users should copy this to their config directory and modify as needed.
"""

import os
from pathlib import Path

# ----------------------------------------------------------------
#                     GENERAL SETTINGS
# ----------------------------------------------------------------

USE_COLOR_LOGS = True
DEBUG_MODE = False

# ----------------------------------------------------------------
#                     PATHS & DIRECTORIES
# ----------------------------------------------------------------

# Base paths
USER_CONFIG_DIR = Path.home() / "Documents" / "DJCLI" / "configuration"
USER_CONTENT_DIR = Path.home() / "Documents" / "DJCLI" / "content"

# Music download paths
DJ_POOL_BASE_PATH = USER_CONTENT_DIR / "download" / "download_music"
DOWNLOAD_FOLDER_NAME = Path.home() / "Downloads"
LINKS_FILE = USER_CONTENT_DIR / "download" / "musicLinks.txt"

# Mixcloud paths
MIXCLOUD_CONTENT_DIR = USER_CONTENT_DIR / "mixcloudContent"
UPLOAD_LINKS_FILE = MIXCLOUD_CONTENT_DIR / "uploadLinks.txt"

# Album cover paths
ALBUM_COVERS_DIR = USER_CONTENT_DIR / "albumCovers"
ORIGINAL_IMAGES_FOLDER = ALBUM_COVERS_DIR / "pexel"
DESTINATION_FOLDER = ALBUM_COVERS_DIR / "pexel_processed"
OUTPUT_FOLDER = ALBUM_COVERS_DIR / "albumCovers_output"

# ----------------------------------------------------------------
#                     API CREDENTIALS
# ----------------------------------------------------------------

# Mixcloud
MIXCLOUD_CLIENT_ID = ""  # Set in .env
MIXCLOUD_CLIENT_SECRET = ""  # Set in .env
MIXCLOUD_PORT = 8001
MIXCLOUD_REDIRECT_URI = f"http://localhost:{MIXCLOUD_PORT}/"
MIXCLOUD_AUTH_URL = (
    "https://www.mixcloud.com/oauth/authorize"
    f"?client_id={MIXCLOUD_CLIENT_ID}&redirect_uri={MIXCLOUD_REDIRECT_URI}"
)

# Spotify
SPOTIFY_CLIENT_ID = ""  # Set in .env
SPOTIFY_CLIENT_SECRET = ""  # Set in .env

# Other APIs
LASTFM_API_KEY = ""  # Set in .env
DEEZER_API_KEY = ""  # Set in .env
MUSICBRAINZ_API_TOKEN = ""  # Set in .env
PEXEL_API_KEY = ""  # Set in .env

# ----------------------------------------------------------------
#                     MIXCLOUD SETTINGS
# ----------------------------------------------------------------

MIXCLOUD_ENABLED = True
MIXCLOUD_PRO_USER = True
MAX_UPLOADS = 8
PUBLISHED_HOUR = 12
PUBLISHED_MINUTE = 0

TRACK_TAGS = [
    "Open Format",
    "Disc Jockey",
    "Live Performance",
    "Katazui",
    "Archive"
]

# ----------------------------------------------------------------
#                     API CONFIGURATIONS
# ----------------------------------------------------------------

APIS = {
    "spotify": {
        "enabled": True,
        "url": "https://api.spotify.com/v1/search",
        "auth_url": "https://accounts.spotify.com/api/token",
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    },
    "deezer": {
        "enabled": True,
        "url": "https://api.deezer.com/search",
        "api_key": DEEZER_API_KEY,
    },
    "lastfm": {
        "enabled": True,
        "api_key": LASTFM_API_KEY,
        "url": "http://ws.audioscrobbler.com/2.0/",
    },
    "musicbrainz": {
        "enabled": True,
        "url": "https://musicbrainz.org/ws/2/recording",
        "cover_art_url": "https://coverartarchive.org/release/",
        "api_token": MUSICBRAINZ_API_TOKEN,
    },
    "mixcloud": {
        "enabled": MIXCLOUD_ENABLED,
        "client_id": MIXCLOUD_CLIENT_ID,
        "client_secret": MIXCLOUD_CLIENT_SECRET,
        "auth_url": MIXCLOUD_AUTH_URL,
    },
    "pexel": {
        "enabled": True,
        "api_key": PEXEL_API_KEY,
        "url": "https://api.pexels.com/v1/search",
    },
}

# ----------------------------------------------------------------
#                     PEXEL SETTINGS
# ----------------------------------------------------------------

PEXEL_TAGS = [
    "minimalist", "simple background", "clean background", "abstract", 
    "white background", "black background", "nature", "landscape", "mountains",
    "forest", "sky", "sea", "beach", "sunset", "sunrise", "desert",
    "cityscape", "urban", "architecture", "buildings", "skyline", "street",
    "texture", "pattern", "fabric", "wood", "marble", "brick", "concrete", "metal",
    "gradient", "blurred background", "soft colors", "pastel colors", "bokeh",
    "aesthetic", "empty space"
]

# ----------------------------------------------------------------
#                     ALBUM COVER SETTINGS
# ----------------------------------------------------------------

PASTE_LOGO = True

"""
Feel free to add or remove any settings as needed. The user can override them
by editing this file once copied to their local config directory.
"""