"""
core/cover_utils.py

Contains functions for:
- Checking if MP3 files have embedded covers
- Fetching album covers via external APIs (Last.fm, MusicBrainz, Deezer, Spotify)
- Downloading, cropping, and embedding album covers
"""

import os
import requests
from io import BytesIO
from typing import Optional, Tuple
from PIL import Image
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from core.color_utils import (
    MSG_ERROR, MSG_NOTICE, MSG_DEBUG, MSG_SUCCESS, MSG_WARNING
)
from config.settings import DEBUG_MODE, APIS
from core.file_utils import log_debug_info

# ----------------------------------------------------------------
#                   HAS EMBEDDED COVER
# ----------------------------------------------------------------

def has_embedded_cover(file_path: str) -> bool:
    """
    Checks whether the MP3 file has an embedded cover (ID3:APIC) tag.
    Returns True if cover art is present, False otherwise.
    """
    try:
        metadata = MP3(file_path, ID3=ID3)
        return bool(metadata and metadata.tags.getall('APIC'))
    except error:
        return False

# ----------------------------------------------------------------
#                 FETCH ALBUM COVER (HIGH-LEVEL)
# ----------------------------------------------------------------

def fetch_album_cover(title: str, artist: str) -> Optional[str]:
    """
    Decide which external API to query to retrieve a cover URL.
    Return the cover URL or None if nothing is found.
    """
    if artist.lower() == "unknown artist" and title.lower() == "unknown title":
        return None

    apis = [
        (lastfm_cover, "Last.fm"),
        (musicbrainz_cover, "MusicBrainz"),
        (spotify_cover, "Spotify"),
        (deezer_cover, "Deezer")
    ]

    for api_func, api_name in apis:
        try:
            if url := api_func(title, artist):
                log_debug_info(f"Found cover from {api_name}")
                return url
        except Exception as e:
            log_debug_info(f"Error fetching cover from {api_name}: {e}")
            continue

    return None

# ----------------------------------------------------------------
#                 LAST.FM COVER
# ----------------------------------------------------------------

def lastfm_cover(title: str, artist: str) -> Optional[str]:
    """Fetch album art from Last.fm API."""
    if not APIS["lastfm"]["enabled"]:
        return None
        
    try:
        params = {
            "method": "track.getInfo",
            "api_key": APIS["lastfm"]["api_key"],
            "artist": artist,
            "track": title,
            "format": "json",
        }
        r = requests.get(APIS["lastfm"]["url"], params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if album_images := data.get("track", {}).get("album", {}).get("image", []):
                return album_images[-1].get("#text")  # Last image is often largest
    except Exception:
        pass
    return None

# ----------------------------------------------------------------
#                MUSICBRAINZ COVER
# ----------------------------------------------------------------

def musicbrainz_cover(title: str, artist: str) -> Optional[str]:
    """Fetch album art from MusicBrainz API."""
    if not APIS["musicbrainz"]["enabled"]:
        return None
        
    try:
        params = {"query": f"recording:{title} AND artist:{artist}", "fmt": "json"}
        r = requests.get(APIS["musicbrainz"]["url"], params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if recordings := data.get("recordings", []):
                if releases := recordings[0].get("releases", []):
                    release_id = releases[0].get("id")
                    return f"{APIS['musicbrainz']['cover_art_url']}{release_id}/front"
    except Exception:
        pass
    return None

# ----------------------------------------------------------------
#                   DEEZER COVER
# ----------------------------------------------------------------

def deezer_cover(title: str, artist: str) -> Optional[str]:
    """Fetch album art from Deezer API."""
    if not APIS["deezer"]["enabled"]:
        return None
        
    try:
        search_url = APIS["deezer"]["url"]
        query = f"{title} {artist}"
        r = requests.get(search_url, params={"q": query}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("data"):
                track = data["data"][0]
                if album := track.get("album", {}):
                    return album.get("cover_big")
    except Exception:
        pass
    return None

# ----------------------------------------------------------------
#                   SPOTIFY COVER
# ----------------------------------------------------------------

def spotify_cover(title: str, artist: str) -> Optional[str]:
    """Fetch album art from Spotify API."""
    if not APIS["spotify"]["enabled"]:
        return None
        
    try:
        from modules.download.downloader import get_spotify_token
        token = get_spotify_token()
        if not token:
            return None

        headers = {"Authorization": f"Bearer {token}"}
        params = {"q": f"{title} {artist}", "type": "track", "limit": 1}
        r = requests.get(APIS["spotify"]["url"], headers=headers, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if items := data.get("tracks", {}).get("items", []):
                if images := items[0].get("album", {}).get("images", []):
                    return images[0].get("url")  # First image is typically largest
    except Exception:
        pass
    return None

# ----------------------------------------------------------------
#           DOWNLOAD + CROP + ATTACH COVER
# ----------------------------------------------------------------

def download_crop_and_attach_cover(file_path: str, cover_url: str) -> bool:
    """
    Download the cover from cover_url, crop it to a square,
    then embed it into the MP3 file as an ID3 APIC frame.
    Returns True if successful, False otherwise.
    """
    try:
        r = requests.get(cover_url, timeout=10)
        if r.status_code != 200:
            print(f"{MSG_ERROR}Failed to download album cover: {r.status_code}")
            return False

        image = Image.open(BytesIO(r.content))
        cropped_image_data = crop_image_to_square(image)
        return attach_cover_to_mp3(file_path, cropped_image_data)
    except Exception as e:
        print(f"{MSG_ERROR}Error attaching cover to {file_path}: {e}")
        return False

def attach_cover_to_mp3(file_path: str, cover_data: bytes) -> bool:
    """
    Embed the given cover_data (JPEG) into the MP3 file as an ID3 APIC frame.
    Returns True if successful, False otherwise.
    """
    try:
        audio = MP3(file_path, ID3=ID3)
        audio.tags.delall('APIC')  # remove existing covers
        audio.tags.add(APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,  # front cover
            desc="Cover",
            data=cover_data,
        ))
        audio.save()
        print(f"{MSG_SUCCESS}Album cover added to {file_path}")
        return True
    except Exception as e:
        print(f"{MSG_ERROR}Failed embedding cover in {file_path}: {e}")
        return False

# ----------------------------------------------------------------
#                 IMAGE CROPPING HELPERS
# ----------------------------------------------------------------

def crop_image_to_square(image: Image.Image) -> bytes:
    """
    Crop the image to a square and convert to JPEG bytes.
    """
    width, height = image.size
    size = min(width, height)
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size
    
    cropped = image.crop((left, top, right, bottom))
    return image_to_jpeg_bytes(cropped)

def image_to_jpeg_bytes(pil_image: Image.Image) -> bytes:
    """
    Convert PIL Image to JPEG bytes.
    """
    buffer = BytesIO()
    pil_image.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()