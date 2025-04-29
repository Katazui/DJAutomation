"""
core/file_utils.py

General file and string utilities:
- Clearing terminal
- Sanitizing filenames
- Removing bracketed text
"""

import os
import re
from typing import Optional
from config.settings import DEBUG_MODE
from core.color_utils import (
    MSG_ERROR, MSG_NOTICE, MSG_WARNING, MSG_STATUS
)


def clear_terminal() -> None:
    """
    Clears the terminal screen on Windows/macOS/Linux.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def sanitize_filename(name: str) -> str:
    """
    Removes characters that are illegal on various operating systems.
    Examples: /, \\, :, *, ?, <, >, |, "
    """
    return re.sub(r'[\/*?:"<>|\\]', '', name)


def remove_unwanted_brackets(text: str) -> str:
    """
    Remove bracketed or parenthetical text unless it contains 'feat' or 'featuring'.
    This removes [Audio Only], [Official Video], (Official Audio), etc.
    But keeps (feat. Artist), (featuring Artist).
    """
    if not text:
        return ""
        
    # Remove parentheses that do NOT contain feat/featuring
    cleaned = re.sub(r'\((?!.*(?:feat|featuring).*).*?\)', '', text, flags=re.IGNORECASE)

    # Remove brackets that do NOT contain feat/featuring
    cleaned = re.sub(r'\[(?!.*(?:feat|featuring).*).*?\]', '', cleaned, flags=re.IGNORECASE)

    return cleaned.strip()


def log_debug_info(message: str) -> None:
    """
    Logs additional debug information if DEBUG_MODE is True.
    """
    if DEBUG_MODE:
        print(f"{MSG_STATUS}(DEBUG) {message}")


def ensure_directory_exists(directory: str) -> bool:
    """
    Ensures a directory exists, creating it if necessary.
    Returns True if successful, False otherwise.
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        log_debug_info(f"Failed to create directory {directory}: {e}")
        return False


# If you have any other file or string manipulation utilities, you can add them here.