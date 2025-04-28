"""
core/metadata_utils.py

Functions for:
- Gleaning artist/title/year/genre from local ID3 tags or external info dicts
- Checking metadata in final MP3s
- Fetching genre from APIs (Last.fm, Deezer, Spotify, MusicBrainz)
"""

import re
import requests
import mutagen
from typing import Tuple, Optional
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, error, TIT2, TPE1, TDRC, TCON
from config.settings import DEBUG_MODE, APIS
from core.color_utils import (
    MSG_ERROR, MSG_NOTICE, MSG_DEBUG, MSG_SUCCESS, MSG_STATUS, MSG_WARNING
)
from core.file_utils import remove_unwanted_brackets, log_debug_info


def parse_title_for_artist_track(youtube_title: str) -> Tuple[str, str]:
    """
    If the YouTube title is in the form 'Artist - Track', split it.
    Otherwise return ('', '').
    """
    if not youtube_title or " - " not in youtube_title:
        return "", ""
        
    parts = youtube_title.split(" - ", 1)
    return parts[0].strip(), parts[1].strip()


def glean_artist_title(file_path: str, info_dict: dict) -> Tuple[str, str]:
    """
    1) Check existing MP3 tags for artist/title
    2) If unknown, parse info_dict
    3) Remove bracketed text that doesn't contain 'feat' or 'featuring'
    4) Return (artist, title)
    """
    try:
        metadata = mutagen.File(file_path, easy=True)
        id3_title = metadata.get('title', [""])[0] if metadata else ""
        id3_artist = metadata.get('artist', [""])[0] if metadata else ""
    except Exception as e:
        log_debug_info(f"Error reading metadata from {file_path}: {e}")
        id3_title, id3_artist = "", ""

    if not id3_title.strip() or id3_title.strip().lower() == "unknown title":
        possible_title = info_dict.get("title", "")
        guess_artist, guess_track = parse_title_for_artist_track(possible_title)

        final_title = guess_track or possible_title or "Unknown Title"
        possible_artist = (
            info_dict.get("artist") or 
            info_dict.get("creator") or 
            info_dict.get("uploader") or 
            "Unknown Artist"
        )
        final_artist = guess_artist or possible_artist

        return (
            remove_unwanted_brackets(final_artist).strip(),
            remove_unwanted_brackets(final_title).strip()
        )

    return (
        remove_unwanted_brackets(id3_artist).strip() or "Unknown Artist",
        remove_unwanted_brackets(id3_title).strip() or "Unknown Title"
    )


def glean_year_genre(info_dict: dict, artist: str, title: str) -> Tuple[str, str]:
    """
    Attempt to glean year from the upload_date if available.
    Attempt to glean genre from info_dict or external APIs.
    """
    raw_year = "Unknown Year"
    if upload_date := info_dict.get("upload_date", ""):
        if len(upload_date) >= 4:
            raw_year = upload_date[:4]

    raw_genre = info_dict.get("genre", "").strip() or "Unknown Genre"
    
    if raw_genre.lower() == "unknown genre":
        if possible_genre := fetch_genre(artist, title):
            raw_genre = possible_genre

    return raw_year, raw_genre


def fetch_genre(artist: str, title: str) -> Optional[str]:
    """
    Attempt to fetch genre from various APIs in order:
    1) Last.fm
    2) Deezer
    3) Spotify
    4) MusicBrainz
    """
    if artist.lower() == "unknown artist" or title.lower() == "unknown title":
        return None

    apis = [
        (lastfm_genre, "Last.fm"),
        (deezer_genre, "Deezer"),
        (spotify_genre, "Spotify"),
        (musicbrainz_genre, "MusicBrainz")
    ]

    for api_func, api_name in apis:
        try:
            if genre := api_func(artist, title):
                log_debug_info(f"Found genre from {api_name}")
                return genre
        except Exception as e:
            log_debug_info(f"Error fetching genre from {api_name}: {e}")
            continue

    return None


def update_id3_tags(file_path: str, artist: str, title: str, year: str, genre: str) -> bool:
    """
    Update the ID3 tags (artist, title, year, genre).
    Returns True if successful, False otherwise.
    """
    try:
        audio = MP3(file_path, ID3=ID3)
        
        # Title & Artist
        audio["TIT2"] = TIT2(encoding=3, text=title)
        audio["TPE1"] = TPE1(encoding=3, text=artist)
        
        # Year & Genre
        audio["TDRC"] = TDRC(encoding=3, text=year or "Unknown Year")
        audio["TCON"] = TCON(encoding=3, text=genre or "Unknown Genre")
        
        audio.save(v2_version=3)
        return True
    except Exception as e:
        print(f"{MSG_ERROR}Could not update ID3 for {file_path}: {str(e)}")
        return False


def check_metadata(file_path: str) -> None:
    """
    Print final ID3 tags: Title, Artist, Year, Genre, 
    and note if cover art is present.
    """
    try:
        audio = MP3(file_path, ID3=ID3)
        
        def get_tag_text(tag):
            return tag.text if hasattr(tag, 'text') else str(tag)
            
        title = get_tag_text(audio.get("TIT2", "No Title"))
        artist = get_tag_text(audio.get("TPE1", "No Artist"))
        year = get_tag_text(audio.get("TDRC", "No Year"))
        genre = get_tag_text(audio.get("TCON", "No Genre"))
        has_art = bool(audio.tags.getall("APIC"))

        print(f"{MSG_NOTICE}Title:      {title}")
        print(f"{MSG_NOTICE}Artist:     {artist}")
        print(f"{MSG_NOTICE}Year:       {year}")
        print(f"{MSG_NOTICE}Genre:      {genre}")
        print(f"{MSG_NOTICE}Cover Art:  {'Present' if has_art else 'None'}")

    except Exception as e:
        print(f"{MSG_ERROR}Error reading metadata from {file_path}: {e}")


# API-specific genre fetching functions
def lastfm_genre(artist: str, title: str) -> Optional[str]:
    """Fetch genre from Last.fm API."""
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
            if genres := data.get("track", {}).get("toptags", {}).get("tag", []):
                return genres[0].get("name")
    except Exception:
        pass
    return None


def deezer_genre(artist: str, title: str) -> Optional[str]:
    """Fetch genre from Deezer API."""
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
                if genre := track.get("genre", {}).get("name"):
                    return genre
    except Exception:
        pass
    return None


def spotify_genre(artist: str, title: str) -> Optional[str]:
    """Fetch genre from Spotify API."""
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
                if genres := items[0].get("album", {}).get("genres", []):
                    return genres[0]
    except Exception:
        pass
    return None


def musicbrainz_genre(artist: str, title: str) -> Optional[str]:
    """Fetch genre from MusicBrainz API."""
    if not APIS["musicbrainz"]["enabled"]:
        return None
        
    try:
        params = {"query": f"recording:{title} AND artist:{artist}", "fmt": "json"}
        r = requests.get(APIS["musicbrainz"]["url"], params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if recordings := data.get("recordings", []):
                if genres := recordings[0].get("genres", []):
                    return genres[0].get("name")
    except Exception:
        pass
    return None