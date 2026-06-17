#!/usr/bin/env python3
"""
cli/main.py

Now includes a 'config' subcommand that:
- Checks API keys from settings.py
- Reads/writes a .env file
- Honors `--set KEY=VALUE` flags to update or add new keys directly from the CLI
- Allows initialization of user_settings.py with --init-settings flag.
- Provides a simple setup command for first-time users
"""

import argparse
import sys
import os
import re
# from djautomation import __version__

# 1) Add the project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    # sys.path.append(project_root)
    sys.path.insert(0, project_root)

# 2) Import modules and settings
from modules.download.downloader import (
    process_links_from_file,
    process_links_interactively
)
from modules.covers.create_album_cover import main as create_album_covers_main, test_run_album_covers
from modules.download.download_pexel import search_and_download_photos
from modules.organize.organize_files import organize_downloads
from cli.mixcloud_cli import handle_mixcloud_subcommand
from core.color_utils import (
    COLOR_GREEN, COLOR_CYAN, COLOR_RESET, COLOR_BLUE, COLOR_YELLOW,
    MSG_STATUS, MSG_NOTICE, MSG_WARNING, MSG_ERROR, LINE_BREAK, MSG_SUCCESS, MSG_DEBUG
)
from config.settings import (
    PEXEL_TAGS, DOWNLOAD_FOLDER_NAME,
    MIXCLOUD_CLIENT_ID, MIXCLOUD_CLIENT_SECRET,
    SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET,
    LASTFM_API_KEY, DEEZER_API_KEY,
    MUSICBRAINZ_API_TOKEN, PEXEL_API_KEY,
    DEBUG_MODE, LINKS_FILE, 
)

from pathlib import Path
from core.version import __version__

def banner():
    return f"""{COLOR_CYAN}
                   _                  _ 
         /\ /\__ _| |_ __ _ _____   _(_)
        / //_/ _` | __/ _` |_  / | | | |
       / __ \ (_| | || (_| |/ /| |_| | |
       \/  \/\__,_|\__\__,_/___|\__,_|_|
**************************************************
*       Welcome to the DJ CLI by Katazui.com     *
*  Control your entire DJ workflow in one place  *
*            Version: {__version__}                *      
**************************************************
{COLOR_RESET}"""

def add_project_root_to_path():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root_dir not in sys.path:
        sys.path.append(root_dir)


def print_loaded_configurations():
    """
    Prints a summary of key loaded configuration values.
    This can be triggered with a flag (like --verbose-config) or always printed
    if DEBUG_MODE is True.
    """
    print(f"{MSG_STATUS}Loaded Settings:")
    print(f"{MSG_DEBUG}DEBUG_MODE: {COLOR_GREEN}{DEBUG_MODE}")
    print(f"  {MSG_NOTICE}API Keys:")
    print(f"    {MSG_DEBUG}MIXCLOUD_CLIENT_ID: {COLOR_GREEN}{MIXCLOUD_CLIENT_ID}")
    print(f"    {MSG_DEBUG}SPOTIFY_CLIENT_ID: {COLOR_GREEN}{SPOTIFY_CLIENT_ID}")
    print(f"    {MSG_DEBUG}LASTFM_API_KEY: {COLOR_GREEN}{LASTFM_API_KEY}")
    # print(f"    {MSG_DEBUG}DEEZER_API_KEY: {DEEZER_API_KEY}")
    # print(f"    {MSG_DEBUG}MUSICBRAINZ_API_TOKEN: {MUSICBRAINZ_API_TOKEN}")
    print(f"    {MSG_DEBUG}PEXEL_API_KEY: {COLOR_GREEN}{PEXEL_API_KEY}")
    
    # Import paths after they're defined
    from config.settings import (
        USER_CONFIG_DIR, USER_CONTENT_DIR, DJ_POOL_BASE_PATH, ALBUM_COVERS_DIR
    )
    
    print(f"  {MSG_NOTICE}Configuration Directories:")
    print(f"    {MSG_DEBUG}Configuration: {COLOR_GREEN}{USER_CONFIG_DIR}")
    print(f"    {MSG_DEBUG}Content: {COLOR_GREEN}{USER_CONTENT_DIR}")
    
    print(f"  {MSG_NOTICE}Content Directories:")
    print(f"    {MSG_DEBUG}DJ Pool: {COLOR_GREEN}{DJ_POOL_BASE_PATH}")
    print(f"    {MSG_DEBUG}Downloads: {COLOR_GREEN}{DOWNLOAD_FOLDER_NAME}")
    print(f"    {MSG_DEBUG}Album Covers: {COLOR_GREEN}{ALBUM_COVERS_DIR}")
    
    print(f"  {MSG_NOTICE}Key Files:")
    print(f"    {MSG_DEBUG}Music Links: {COLOR_GREEN}{LINKS_FILE}")
    print(LINE_BREAK)


# ----------------------------------------------------------------
#          Existing Subcommand Handlers
# ----------------------------------------------------------------

def handle_download_music_subcommand(args):
    if args.mode == "interactive":
        process_links_interactively()
    else:
        process_links_from_file()

    if args.organize:
        print(f"{MSG_NOTICE}Organizing downloaded files...")
        organize_downloads(requested=False)

def handle_download_pexel_subcommand(args):
    from config.settings import USER_CONTENT_DIR
    folder_path = USER_CONTENT_DIR / 'albumCovers' / 'pexel'
    log_path = USER_CONTENT_DIR / 'albumCovers' / 'downloaded_pexel_photos.txt'
    folder_path.mkdir(parents=True, exist_ok=True)
    
    search_and_download_photos(
        tags=PEXEL_TAGS,
        total_photos=args.num_photos,
        folder=str(folder_path),
        log_file=str(log_path)
    )

def handle_organize_subcommand(args):
    if not os.path.exists(DOWNLOAD_FOLDER_NAME):
        print(f"{MSG_WARNING}Download folder '{DOWNLOAD_FOLDER_NAME}' not found.")
        return

    if args.requested:
        print(f"{MSG_NOTICE}Organizing only requested songs...")
        # Add your specific logic for requested songs here.
    else:
        print(f"{MSG_NOTICE}Organizing all downloaded files...")
        organize_downloads()

def handle_create_album_covers_subcommand(args):
    if args.test:
        print(f"{MSG_NOTICE}Running test mode for album covers...")
        test_run_album_covers()
    else:
        create_album_covers_main()

def handle_config_subcommand(args):
    """
    Handles the configuration subcommand. Processes .env updates, and,
    if --init-settings is specified, creates user_settings.py in the
    user configuration folder.
    """
    dotenv_path = Path(project_root) / ".env"
    
    # Setup mode - streamlined onboarding for new users
    if args.setup:
        return setup_config_wizard(dotenv_path)
    
    env_dict = parse_env_file(dotenv_path)

    changed_anything = False
    updated_keys = {}

    if args.mc_id is not None:
        env_dict["MIXCLOUD_CLIENT_ID"] = args.mc_id
        updated_keys["MIXCLOUD_CLIENT_ID"] = args.mc_id
    if args.mc_secret is not None:
        env_dict["MIXCLOUD_CLIENT_SECRET"] = args.mc_secret
        updated_keys["MIXCLOUD_CLIENT_SECRET"] = args.mc_secret
    if args.spotify_id is not None:
        env_dict["SPOTIFY_CLIENT_ID"] = args.spotify_id
        updated_keys["SPOTIFY_CLIENT_ID"] = args.spotify_id
    if args.spotify_secret is not None:
        env_dict["SPOTIFY_CLIENT_SECRET"] = args.spotify_secret
        updated_keys["SPOTIFY_CLIENT_SECRET"] = args.spotify_secret
    if args.lastfm is not None:
        env_dict["LASTFM_API_KEY"] = args.lastfm
        updated_keys["LASTFM_API_KEY"] = args.lastfm
    if args.deezer is not None:
        env_dict["DEEZER_API_KEY"] = args.deezer
        updated_keys["DEEZER_API_KEY"] = args.deezer
    if args.musicbrainz is not None:
        env_dict["MUSICBRAINZ_API_TOKEN"] = args.musicbrainz
        updated_keys["MUSICBRAINZ_API_TOKEN"] = args.musicbrainz
    if args.pexel is not None:
        env_dict["PEXEL_API_KEY"] = args.pexel
        updated_keys["PEXEL_API_KEY"] = args.pexel

    if updated_keys:
        changed_anything = True
        write_env_file(dotenv_path, env_dict)
        for k, v in updated_keys.items():
            print(f"{MSG_NOTICE}Set {k}={v} in .env")

    # Init user settings
    if args.init_settings:
        init_user_settings()
    
    # Show current config
    if args.show:
        print_loaded_configurations()


def setup_config_wizard(dotenv_path):
    """
    Interactive wizard to guide new users through the DJ Automation setup.
    """
    print(f"{COLOR_CYAN}========================================")
    print(f"   DJ Automation - First Time Setup   ")
    print(f"========================================{COLOR_RESET}")
    print(f"This wizard will guide you through setting up DJ Automation.")
    print(f"You'll need to provide API keys for various services.")
    print(f"You can skip any step and configure it later.\n")
    
    # Initialize configs
    init_user_settings()
    
    # Read existing environment
    env_dict = parse_env_file(dotenv_path)
    
    # Collect API keys
    print(f"{COLOR_CYAN}API Configuration:{COLOR_RESET}")
    
    # Get Mixcloud credentials
    mixcloud_id = input(f"Mixcloud Client ID [{env_dict.get('MIXCLOUD_CLIENT_ID', '')}]: ").strip()
    if mixcloud_id:
        env_dict["MIXCLOUD_CLIENT_ID"] = mixcloud_id
    
    mixcloud_secret = input(f"Mixcloud Client Secret [{env_dict.get('MIXCLOUD_CLIENT_SECRET', '')}]: ").strip()
    if mixcloud_secret:
        env_dict["MIXCLOUD_CLIENT_SECRET"] = mixcloud_secret
    
    # Get Spotify credentials
    spotify_id = input(f"Spotify Client ID [{env_dict.get('SPOTIFY_CLIENT_ID', '')}]: ").strip()
    if spotify_id:
        env_dict["SPOTIFY_CLIENT_ID"] = spotify_id
    
    spotify_secret = input(f"Spotify Client Secret [{env_dict.get('SPOTIFY_CLIENT_SECRET', '')}]: ").strip()
    if spotify_secret:
        env_dict["SPOTIFY_CLIENT_SECRET"] = spotify_secret
    
    # Get Last.fm API key
    lastfm_key = input(f"Last.fm API Key [{env_dict.get('LASTFM_API_KEY', '')}]: ").strip()
    if lastfm_key:
        env_dict["LASTFM_API_KEY"] = lastfm_key
    
    # Get Pexel API key
    pexel_key = input(f"Pexel API Key [{env_dict.get('PEXEL_API_KEY', '')}]: ").strip()
    if pexel_key:
        env_dict["PEXEL_API_KEY"] = pexel_key
    
    # Save to .env file
    write_env_file(dotenv_path, env_dict)
    
    print(f"\n{MSG_SUCCESS}Configuration completed successfully!")
    print(f"{MSG_NOTICE}User configuration directory: {Path.home() / 'Documents' / 'DJCLI' / 'configuration'}")
    print(f"{MSG_NOTICE}User content directory: {Path.home() / 'Documents' / 'DJCLI' / 'content'}")
    print(f"\nRun {COLOR_GREEN}dj config --show{COLOR_RESET} to see your current configuration.")


def init_user_settings():
    """Initialize user settings files"""
    try:
        # Import locally to avoid circular imports
        from config import USER_CONFIG_DIR, ensure_config_file
        
        # Initialize user configuration files
        user_settings_path = ensure_config_file(
            "default_settings.py", 
            USER_CONFIG_DIR / "user_settings.py"
        )
        
        # Initialize album cover config
        album_config_path = ensure_config_file(
            "default_albumCoverConfig.json",
            USER_CONFIG_DIR / "albumCoverConfig.json"
        )
        
        print(f"{MSG_SUCCESS}User settings initialized:")
        print(f"  - Settings: {user_settings_path}")
        print(f"  - Album covers: {album_config_path}")
        
    except Exception as e:
        print(f"{MSG_ERROR}Failed to initialize user settings: {e}")

# ----------------------------------------------------------------
#          Utility Functions
# ----------------------------------------------------------------

def parse_env_file(env_path):
    if not os.path.exists(env_path):
        return {}
    env_dict = {}
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r'([^=]+)=(.*)', line)
            if match:
                key = match.group(1).strip()
                val = match.group(2).strip()
                env_dict[key] = val
    return env_dict

def write_env_file(env_path, env_dict):
    with open(env_path, "w", encoding="utf-8") as f:
        for key, val in env_dict.items():
            f.write(f"{key}={val}\n")

def setup_argparser():
    parser = argparse.ArgumentParser(
        prog="djcli",
        description="https://github.com/Katazui/DJAutomation",
        epilog=f"{COLOR_GREEN}Tip:{COLOR_RESET} Use 'djcli config --mc_id YOUR_ID --init-settings' to update .env and initialize user settings."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Download Music
    download_music_parser = subparsers.add_parser("dl_audio", help="Download audio from Youtube/SoundCloud links.")
    download_music_parser.add_argument("--mode",
        choices=["interactive", "file"],
        default="interactive",
        help="Download mode. Default=interactive"
    )
    download_music_parser.add_argument("--organize",
        action="store_true",
        help="Organize after download."
    )

    # Organize
    organize_parser = subparsers.add_parser("org_dl", help="Organize downloaded audio files.")
    organize_parser.add_argument("--requested",
        action="store_true",
        help="Only organize requested songs."
    )

    # Download Pexels
    download_pexel_parser = subparsers.add_parser("dl_pexel", help="Download photos from Pexels.")
    download_pexel_parser.add_argument("--num_photos",
        type=int,
        default=5,
        help="Number of photos per tag. Default=5."
    )

    # Covers
    covers_parser = subparsers.add_parser("create_ac", help="Create album covers from images.")
    covers_parser.add_argument("--test", action="store_true", help="Test mode for creating album covers.")

    # Mixcloud Upload
    mixcloud_parser = subparsers.add_parser("up_mixes", help="Upload multiple tracks to Mixcloud.")
    mixcloud_parser.add_argument("--init-settings", action="store_true", help="Initialize MixCloud Content.")
    mixcloud_parser.add_argument("--dry-run", action="store_true", help="Dry run mode for Mixcloud uploads.")

    # Testing
    test_parser = subparsers.add_parser("test", help="Run tests.")
    test_parser.add_argument("--mixcloud", action="store_true", 
                            help="Run tests for Mixcloud module only")
    test_parser.add_argument("--download", action="store_true", 
                            help="Run tests for download module only")

    # Config
    config_parser = subparsers.add_parser("config", help="Check or set API keys in .env and manage user settings.")
    config_parser.add_argument("--print", action="store_true", help="Print loaded configurations.")
    config_parser.add_argument("--mc_id",       type=str, help="Set Mixcloud Client ID.")
    config_parser.add_argument("--mc_secret",   type=str, help="Set Mixcloud Client Secret.")
    config_parser.add_argument("--spotify_id",  type=str, help="Set Spotify Client ID.")
    config_parser.add_argument("--spotify_secret", type=str, help="Set Spotify Client Secret.")
    config_parser.add_argument("--lastfm",      type=str, help="Set Last.fm API key.")
    config_parser.add_argument("--deezer",      type=str, help="Set Deezer API key.")
    config_parser.add_argument("--musicbrainz", type=str, help="Set MusicBrainz token.")
    config_parser.add_argument("--pexel",       type=str, help="Set Pexel API key.")
    config_parser.add_argument("--init-settings", action="store_true", help="Initialize (create) user_settings.py in the configuration folder.")
    config_parser.add_argument("--setup",         action="store_true", help="Run setup wizard.")
    config_parser.add_argument("--show",          action="store_true", help="Show current configuration.")


    return parser

# ----------------------------------------------------------------
#          Main Function for CLI
# ----------------------------------------------------------------

def main():
    # Add project root to path
    add_project_root_to_path()

    # Load configuration
    try:
        from config import USER_CONFIG_DIR, USER_SETTINGS
        print(f"{MSG_STATUS}Loaded configuration from: {USER_CONFIG_DIR}")
    except Exception as e:
        print(f"{MSG_ERROR}Error loading configuration: {e}")

    print(banner())

    parser = setup_argparser()
    args = parser.parse_args()

    if DEBUG_MODE or (hasattr(args, "verbose_config") and args.verbose_config):
        print_loaded_configurations()

    if not args.command:
        parser.print_help()
        return

    if args.command == "dl_audio":
        print(f"{MSG_STATUS}Starting 'download_music' subcommand...\n{LINE_BREAK}")
        handle_download_music_subcommand(args)

    elif args.command == "dl_pexel":
        print(f"{MSG_STATUS}Starting 'download_pexel' subcommand...\n{LINE_BREAK}")
        handle_download_pexel_subcommand(args)

    elif args.command == "create_ac":
        print(f"{MSG_STATUS}Starting 'create album covers' subcommand...\n{LINE_BREAK}")
        handle_create_album_covers_subcommand(args)

    elif args.command == "org_dl":
        print(f"{MSG_STATUS}Starting 'organize download' subcommand...\n{LINE_BREAK}")
        handle_organize_subcommand(args)

    elif args.command == "up_mixes":
        print(f"{MSG_STATUS}Starting 'upload mixcloud mixes' subcommand...\n{LINE_BREAK}")
        handle_mixcloud_subcommand(args)

    elif args.command == "test":
        print(f"{MSG_STATUS}Running custom tests or debug checks...\n{LINE_BREAK}")
        from cli.test_cli import handle_test_subcommand
        handle_test_subcommand(args)

    elif args.command == "config":
        print(f"{MSG_STATUS}Starting 'config' subcommand...\n{LINE_BREAK}")
        handle_config_subcommand(args)

    else:
        print(f"{MSG_ERROR}Unknown subcommand: {args.command}")
        parser.print_help()

if __name__ == "__main__":
    main()