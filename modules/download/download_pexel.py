# modules/download/download_pexel.py

import os
import requests
import random
import time
from pathlib import Path
from config.settings import (
    PEXEL_API_KEY, 
    PEXEL_TAGS, 
    APIS, 
    USER_CONTENT_DIR,
)
from core.color_utils import (
    COLOR_GREEN, COLOR_RED, COLOR_YELLOW, COLOR_RESET,
    MSG_NOTICE, MSG_ERROR, MSG_SUCCESS
)

# Define constants
PEXEL_API_URL = APIS["pexel"]["url"]
PEXEL_DOWNLOAD_FOLDER = USER_CONTENT_DIR / "albumCovers" / "pexel"
PEXEL_LOG_FILE = USER_CONTENT_DIR / "albumCovers" / "downloaded_pexel_photos.txt"

# Headers for the Pexels API request
headers = {
    'Authorization': PEXEL_API_KEY
}


def download_photo(url, folder, photo_id):
    """
    Downloads a single photo from the given URL and saves it to the specified folder.
    
    Parameters:
    - url (str): URL of the photo to download.
    - folder (str): Destination folder to save the photo.
    - photo_id (str): Unique identifier for the photo.
    """
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            os.makedirs(folder, exist_ok=True)  # Ensure the download folder exists
            with open(os.path.join(folder, f'{photo_id}.jpg'), 'wb') as f:
                for chunk in response.iter_content(1024):
                    if chunk:
                        f.write(chunk)
            print(f"{MSG_SUCCESS}Downloaded photo {photo_id}")
        else:
            print(f"Failed to download photo {photo_id} | Status Code: {response.status_code}")
    except Exception as e:
        print(f"Exception occurred while downloading photo {photo_id}: {e}")

def read_downloaded_photo_ids(file_path):
    """
    Reads the log file and returns a set of already downloaded photo IDs.
    
    Parameters:
    - file_path (str): Path to the log file.
    
    Returns:
    - set: A set containing downloaded photo IDs.
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return set(line.strip() for line in f)
        except Exception as e:
            print(f"Exception occurred while reading log file {file_path}: {e}")
            return set()
    return set()

def write_downloaded_photo_ids(file_path, photo_ids):
    """
    Appends newly downloaded photo IDs to the log file.
    
    Parameters:
    - file_path (str): Path to the log file.
    - photo_ids (set): Set of newly downloaded photo IDs.
    """
    try:
        # Ensure the parent directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'a') as f:
            for photo_id in photo_ids:
                f.write(f"{photo_id}\n")
    except Exception as e:
        print(f"{MSG_ERROR}Exception occurred while writing to log file {file_path}: {e}")

def search_and_download_photos(tags=None, total_photos=5, folder=None, log_file=None):
    """
    Downloads a total of `total_photos` from Pexels by randomly selecting tags.
    
    Parameters:
    - tags (list): List of tags to search for photos.
    - total_photos (int): Total number of photos to download.
    - folder (str): Destination folder for downloaded photos.
    - log_file (str): Path to the log file for tracking downloaded photo IDs.
    """
    # Use default values if not provided
    tags = tags or PEXEL_TAGS
    folder = folder or str(PEXEL_DOWNLOAD_FOLDER)
    log_file = log_file or str(PEXEL_LOG_FILE)
    
    if not PEXEL_API_KEY:
        print(f"{MSG_ERROR}PEXEL_API_KEY is not set. Please add it to your .env file.")
        return

    # Read already downloaded photo IDs to avoid duplicates
    downloaded_photo_ids = read_downloaded_photo_ids(log_file)
    new_downloaded_photo_ids = set()
    photos_downloaded = 0

    # Shuffle the tags to ensure randomness
    available_tags = tags.copy()
    random.shuffle(available_tags)

    while photos_downloaded < total_photos and available_tags:
        tag = random.choice(available_tags)
        page = random.randint(1, 100)  # Start with a random page

        params = {
            'query': tag,
            'per_page': min(80, total_photos - photos_downloaded),  # Max per_page is 80
            'page': page
        }

        try:
            response = requests.get(PEXEL_API_URL, headers=headers, params=params)
        except requests.exceptions.RequestException as e:
            print(f"{MSG_ERROR}Request exception for tag '{tag}': {e}")
            # Optionally, remove the tag to avoid repeated failures
            available_tags.remove(tag)
            continue

        if response.status_code == 200:
            data = response.json()
            photos = data.get('photos', [])
            
            if not photos:
                print(f"{MSG_ERROR}No photos found for tag: {tag}")
                # Optionally, remove the tag if no photos are found
                available_tags.remove(tag)
                continue

            for photo in photos:
                photo_url = photo['src']['original']
                photo_id = str(photo['id'])
                if photo_id not in downloaded_photo_ids and photo_id not in new_downloaded_photo_ids:
                    download_photo(photo_url, folder, photo_id)
                    new_downloaded_photo_ids.add(photo_id)
                    photos_downloaded += 1
                    if photos_downloaded >= total_photos:
                        break
                else:
                    print(f"{MSG_NOTICE}Skipping already downloaded photo {photo_id}")

            # To avoid hitting rate limits
            time.sleep(1)  # Sleep for 1 second between requests

        elif response.status_code == 429:
            print(f"[Error]: Rate limit exceeded for tag: {tag}. Sleeping for 60 seconds...")
            time.sleep(60)
        else:
            print(f"[Error]: Failed to search for tag: {tag} | Status Code: {response.status_code} | Response: {response.text}")
            # Optionally, remove the tag to avoid repeated failures
            available_tags.remove(tag)

    # Write the newly downloaded photo IDs to the log file
    write_downloaded_photo_ids(log_file, new_downloaded_photo_ids)
    print(f"{MSG_SUCCESS}{len(new_downloaded_photo_ids)} new photos downloaded and logged to {log_file}")

if __name__ == "__main__":
    # This allows you to run the script directly for testing purposes
    import sys

    try:
        num_photos = int(input("How many photos do you want to download in total? "))
        if num_photos <= 0:
            raise ValueError
    except ValueError:
        print("[Error]: Please enter a valid positive integer for the number of photos.")
        sys.exit(1)

    print(f"Tags to be used: {', '.join(PEXEL_TAGS)}")
    print(f"Downloading {num_photos} photos in total from Pexels.")
    search_and_download_photos(tags=PEXEL_TAGS, total_photos=num_photos)