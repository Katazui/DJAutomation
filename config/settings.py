"""
config/settings.py

Central configuration for DJ Automation.
Handles all settings, paths, and API configurations.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ----------------------------------------------------------------
#                     BASE PATHS
# ----------------------------------------------------------------

CONFIG_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = CONFIG_DIR.parent
USER_CONFIG_DIR = Path.home() / "Documents" / "DJCLI" / "configuration"
USER_CONTENT_DIR = Path.home() / "Documents" / "DJCLI" / "content"

# ----------------------------------------------------------------
#                     COLOR CODES
# ----------------------------------------------------------------

COLOR_RESET = "\033[0m"
COLOR_RED = "\033[31m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_BLUE = "\033[34m"
COLOR_PURPLE = "\033[35m"
COLOR_CYAN = "\033[36m"
COLOR_GREY = "\033[37m"

# ----------------------------------------------------------------
#                     MESSAGE PREFIXES
# ----------------------------------------------------------------

MSG_ERROR = f"{COLOR_RED}[Error]{COLOR_RESET}: "
MSG_NOTICE = f"{COLOR_YELLOW}[Notice]{COLOR_RESET}: "
MSG_DEBUG = f"{COLOR_CYAN}[Debug]{COLOR_RESET}: "
MSG_SUCCESS = f"{COLOR_GREEN}[Success]{COLOR_RESET}: "
MSG_STATUS = f"{COLOR_GREEN}[Status]{COLOR_RESET}: "
MSG_WARNING = f"{COLOR_BLUE}[Warning]{COLOR_RESET}: "
LINE_BREAK = f"{COLOR_GREY}----------------------------------------{COLOR_RESET}"

# ----------------------------------------------------------------
#                     GENERAL SETTINGS
# ----------------------------------------------------------------

USE_COLOR_LOGS = os.getenv("USE_COLOR_LOGS", "True").lower() == "true"
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# ----------------------------------------------------------------
#                     PATHS & DIRECTORIES
# ----------------------------------------------------------------

# Music download paths
DJ_POOL_BASE_PATH = Path(os.getenv(
    "DJ_POOL_BASE_PATH",
    USER_CONTENT_DIR / "download" / "download_music"
))
DOWNLOAD_FOLDER_NAME = Path(os.getenv(
    "DOWNLOAD_FOLDER_NAME",
    Path.home() / "Downloads"
))
LINKS_FILE = Path(os.getenv(
    "LINKS_FILE",
    USER_CONTENT_DIR / "download" / "musicLinks.txt"
))

# Mixcloud paths
MIXCLOUD_CONTENT_DIR = USER_CONTENT_DIR / "mixcloudContent"
UPLOAD_LINKS_FILE = Path(os.getenv(
    "UPLOAD_LINKS_FILE",
    MIXCLOUD_CONTENT_DIR / "uploadLinks.txt"
))

# Album cover paths
ALBUM_COVERS_DIR = USER_CONTENT_DIR / "albumCovers"
ORIGINAL_IMAGES_FOLDER = ALBUM_COVERS_DIR / "pexel"
DESTINATION_FOLDER = ALBUM_COVERS_DIR / "pexel_processed"
OUTPUT_FOLDER = ALBUM_COVERS_DIR / "albumCovers_output"

# ----------------------------------------------------------------
#                     API CREDENTIALS
# ----------------------------------------------------------------

# Mixcloud
MIXCLOUD_CLIENT_ID = os.getenv("MIXCLOUD_CLIENT_ID", "")
MIXCLOUD_CLIENT_SECRET = os.getenv("MIXCLOUD_CLIENT_SECRET", "")
MIXCLOUD_PORT = int(os.getenv("MIXCLOUD_PORT", "8001"))
MIXCLOUD_REDIRECT_URI = f"http://localhost:{MIXCLOUD_PORT}/"
MIXCLOUD_AUTH_URL = (
    "https://www.mixcloud.com/oauth/authorize"
    f"?client_id={MIXCLOUD_CLIENT_ID}&redirect_uri={MIXCLOUD_REDIRECT_URI}"
)

# Spotify
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")

# Other APIs
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY", "")
DEEZER_API_KEY = os.getenv("DEEZER_API_KEY", "")
MUSICBRAINZ_API_TOKEN = os.getenv("MUSICBRAINZ_API_TOKEN", "")
PEXEL_API_KEY = os.getenv("PEXEL_API_KEY", "")

# ----------------------------------------------------------------
#                     MIXCLOUD SETTINGS
# ----------------------------------------------------------------

MIXCLOUD_ENABLED = True
MIXCLOUD_PRO_USER = True
MAX_UPLOADS = int(os.getenv("MAX_UPLOADS", "8"))
PUBLISHED_HOUR = int(os.getenv("PUBLISHED_HOUR", "12"))
PUBLISHED_MINUTE = int(os.getenv("PUBLISHED_MINUTE", "00"))

# Mixcloud content paths
USE_EXTERNAL_TRACK_DIR = os.getenv("USE_EXTERNAL_TRACK_DIR", "False").lower() == "true"
LOCAL_TRACK_DIR = USER_CONTENT_DIR / "mixcloudContent" / "tracks"
EXTERNAL_TRACK_DIR = Path(os.getenv("EXTERNAL_TRACK_DIR", str(LOCAL_TRACK_DIR)))
COVER_IMAGE_DIRECTORY = USER_CONTENT_DIR / "mixcloudContent" / "covers"
FINISHED_DIRECTORY = USER_CONTENT_DIR / "mixcloudContent" / "finished"
TITLES_FILE = USER_CONTENT_DIR / "mixcloudContent" / "titles.txt"
PUBLISHED_DATES = USER_CONTENT_DIR / "mixcloudContent" / "published_dates.json"

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

APIS: Dict[str, Dict[str, Any]] = {
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

# Load album cover configuration
try:
    from . import ALBUM_COVER_CONFIG
    GLOBAL_SETTINGS = ALBUM_COVER_CONFIG.get("GLOBAL_SETTINGS", {})
    CONFIGURATIONS = ALBUM_COVER_CONFIG.get("CONFIGURATIONS", {})
    PASTE_LOGO = GLOBAL_SETTINGS.get("PASTE_LOGO", True)
except ImportError:
    GLOBAL_SETTINGS = {}
    CONFIGURATIONS = {}
    PASTE_LOGO = True
