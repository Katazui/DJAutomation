"""
config/__init__.py

Configuration initialization and management for DJ Automation.
Handles loading of settings, environment variables, and user configurations.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
CONFIG_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = CONFIG_DIR.parent
USER_CONFIG_DIR = Path.home() / "Documents" / "DJCLI" / "configuration"
USER_CONTENT_DIR = Path.home() / "Documents" / "DJCLI" / "content"

# Ensure user directories exist
USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
USER_CONTENT_DIR.mkdir(parents=True, exist_ok=True)

def ensure_config_file(source_file: str, dest_file: Path) -> Path:
    """
    Ensures a configuration file exists in the user's config directory.
    If it doesn't exist, copies the default from the package.
    """
    if not dest_file.exists():
        try:
            shutil.copy2(CONFIG_DIR / source_file, dest_file)
            print(f"Created user config at: {dest_file}")
        except Exception as e:
            print(f"Error creating config file {dest_file}: {e}")
            raise
    return dest_file

def load_json_config(source_file: str, dest_file: Path) -> Dict[str, Any]:
    """
    Loads a JSON configuration file, creating it from default if needed.
    """
    config_path = ensure_config_file(source_file, dest_file)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        return {}

def load_py_config(source_file: str, dest_file: Path) -> Dict[str, Any]:
    """
    Loads a Python configuration file, creating it from default if needed.
    """
    config_path = ensure_config_file(source_file, dest_file)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return eval(f.read())
    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        return {}

# Initialize configurations
ALBUM_COVER_CONFIG = load_json_config(
    "default_albumCoverConfig.json",
    USER_CONFIG_DIR / "albumCoverConfig.json"
)

USER_SETTINGS = load_py_config(
    "default_settings.py",
    USER_CONFIG_DIR / "user_settings.py"
)

# Export commonly used settings
from .settings import *  # noqa