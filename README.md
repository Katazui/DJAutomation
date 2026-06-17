# 🎧 DJ Automation CLI

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python Tests](https://github.com/Katazui/DJAutomation/actions/workflows/python-tests.yml/badge.svg)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/Katazui/DJAutomation.svg)
![Repo Size](https://img.shields.io/github/repo-size/Katazui/DJAutomation.svg)
![GitHub Release](https://img.shields.io/github/release/Katazui/DJAutomation.svg)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Donate-yellow.svg?style=flat)](https://buymeacoffee.com/katazui)
![GitHub Forks](https://img.shields.io/github/forks/Katazui/DJAutomation?style=social&label=Fork)
![GitHub Stars](https://img.shields.io/github/stars/Katazui/DJAutomation?style=social&label=Stars)

![DJ Automation Banner](https://katazui.com/wp-content/uploads/2023/07/Katazui-Logo-1-300x188.png)

Welcome to the **DJ Automation CLI**! This powerful tool streamlines your DJ workflow by automating tasks such as downloading tracks, organizing files, generating album covers, and uploading mixes to Mixcloud. Whether you're managing a personal collection or handling large-scale uploads, this CLI has got you covered. 🚀

[![Buy Me A Coffee](https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png)](https://buymeacoffee.com/katazui)

---

## 📜 Table of Contents

- [🎧 DJ Automation CLI](#-dj-automation-cli)
  - [📜 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🗂️ Project Structure](#️-project-structure)
  - [⚙️ Configuration](#️-configuration)
    - [📄 `.env` File](#-env-file)
    - [🛠️ Configuration Setup](#️-configuration-setup)
  - [🚀 Installation](#-installation)
    - [Building the DJCLI Executable](#building-the-djcli-executable)
  - [🔧 Usage](#-usage)
    - [📥 Download Tracks](#-download-tracks)
    - [🎨 Create Album Covers](#-create-album-covers)
    - [📂 Organize Files](#-organize-files)
    - [☁️ Upload to Mixcloud](#️-upload-to-mixcloud)
    - [🧪 Run Tests](#-run-tests)
  - [📚 Modules Overview](#-modules-overview)
  - [🔒 Security](#-security)
  - [📞 Support](#-support)
  - [📝 License](#-license)
  - [🙏 Contributing](#-contributing)

---

## ✨ Features

- **Automated Downloads**: Fetch audio tracks from various sources effortlessly.
- **File Organization**: Automatically organize your downloads for easy access.
- **Album Cover Generation**: Create stunning album covers for your mixes.
- **Mixcloud Integration**: Seamlessly upload your mixes to Mixcloud with OAuth authentication.
- **Scheduling**: Schedule uploads to publish your mixes at optimal times.
- **Robust Testing**: Ensure reliability with comprehensive automated tests.
- **Colorful CLI**: Enjoy an intuitive and visually appealing command-line interface with color-coded messages. 🎨

---

## 🗂️ Project Structure

```
DJAutomation/
│
├── cli/
│   ├── main.py              # Main CLI entry point
│   ├── mixcloud_cli.py      # Mixcloud-specific CLI functions
│   ├── test_cli.py          # CLI for running tests
│   ├── download_cli.py      # Download-specific CLI functions
│   └── organize_cli.py      # Organization-specific CLI functions
│
├── config/
│   ├── settings.py          # Main configuration settings
│   ├── default_settings.py  # Default configuration template
│   ├── default_albumCoverConfig.json  # Default album cover settings
│   └── albumCoverConfig.json  # User album cover settings
│
├── core/
│   ├── color_utils.py       # Utilities for colored CLI messages
│   ├── file_utils.py        # File handling utilities
│   ├── metadata_utils.py    # Metadata handling utilities
│   └── cover_utils.py       # Album cover utilities
│
├── modules/
│   ├── download/
│   │   ├── downloader.py    # Module for downloading tracks
│   │   └── download_pexel.py # Module for downloading images
│   │
│   ├── covers/
│   │   └── create_album_cover.py # Module for creating album covers
│   │
│   ├── organize/
│   │   └── organize_files.py # Module for organizing files
│   │
│   └── mixcloud/
│       └── uploader.py      # Module for uploading to Mixcloud
│
├── tests/
│   └── test_mixcloud.py     # Tests for Mixcloud uploader
│
├── .env                     # Environment variables (not committed)
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup file
└── README.md                # Project documentation
```

---

## ⚙️ Configuration

### 📄 `.env` File

All sensitive credentials and environment-specific settings are managed through the `.env` file. **Ensure this file is listed in your `.gitignore` to prevent accidental commits of sensitive information.**

#### 📌 Sample `.env`:

```dotenv
# Mixcloud OAuth
MIXCLOUD_CLIENT_ID=""
MIXCLOUD_CLIENT_SECRET=""

# Spotify
SPOTIFY_CLIENT_ID=""
SPOTIFY_CLIENT_SECRET=""

# Last.fm
LASTFM_API_KEY=""

# Deezer
DEEZER_API_KEY=""

# MusicBrainz
MUSICBRAINZ_API_TOKEN=""

# Pexel
PEXEL_API_KEY=""

# General Settings
DEBUG_MODE=False
USE_COLOR_LOGS=True
```

### 🛠️ Configuration Setup

The easiest way to set up your configuration is to use the built-in setup wizard:

```bash
dj config --setup
```

This will guide you through:

1. Creating necessary configuration directories
2. Setting up default configuration files
3. Entering your API keys
4. Configuring paths and settings

You can also manually configure settings by editing the files in `~/Documents/DJCLI/configuration/`.

---

## 🚀 Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Katazui/DJAutomation.git
   cd DJAutomation
   ```

2. **Create a Virtual Environment** (recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Install the Package**:

   ```bash
   pip install -e .
   ```

5. **Run the Setup Wizard**:

   ```bash
   python cli/main.py config --setup
   ```

### Building the DJCLI Executable

To build a standalone executable for the DJCLI:

1. **Install PyInstaller**:

   ```bash
   pip install pyinstaller
   ```

2. **Build the Executable**:

   ```bash
   # For macOS/Linux
   pyinstaller --onefile --name dj cli/main.py

   # For Windows
   pyinstaller --onefile --name dj.exe cli/main.py
   ```

3. **Move the Executable**:

   ```bash
   # For macOS/Linux
   mv dist/dj /usr/local/bin/

   # For Windows
   # Move dist/dj.exe to a directory in your PATH
   ```

4. **Verify Installation**:

   ```bash
   dj --version
   ```

5. **Configure the Executable**:

   ```bash
   dj config --setup
   ```

**Note**: The executable will be created in the `dist` directory. Make sure to move it to a location in your system's PATH for easy access.

---

## 🔧 Usage

### 📥 Download Tracks

Download tracks from YouTube/SoundCloud links:

```bash
# Interactive mode
dj dl_audio

# File mode (reads from musicLinks.txt)
dj dl_audio --mode file

# Download and organize
dj dl_audio --organize
```

### 🎨 Create Album Covers

Generate album covers from images:

```bash
# Normal mode
dj create_ac

# Test mode
dj create_ac --test
```

### 📂 Organize Files

Organize downloaded files:

```bash
# Organize all files
dj org_dl

# Organize only requested files
dj org_dl --requested
```

### ☁️ Upload to Mixcloud

Upload mixes to Mixcloud:

```bash
# Initialize Mixcloud settings
dj up_mixes --init-settings

# Upload mixes
dj up_mixes

# Dry run (no actual upload)
dj up_mixes --dry-run
```

### 🧪 Run Tests

Run tests to ensure everything is working correctly:

```bash
# Run all tests
dj test

# Run specific tests
dj test --mixcloud
dj test --download
```

---

## 📚 Modules Overview

### 🔍 Download Module

- **downloader.py**: Handles downloading audio tracks from various sources
- **download_pexel.py**: Downloads images from Pexels for album covers

### 🎨 Covers Module

- **create_album_cover.py**: Creates album covers from downloaded images

### 📂 Organize Module

- **organize_files.py**: Organizes downloaded files into structured directories

### ☁️ Mixcloud Module

- **uploader.py**: Manages uploading tracks to Mixcloud

### 🛠️ Core Module

- **color_utils.py**: CLI color utilities
- **file_utils.py**: File handling utilities
- **metadata_utils.py**: Metadata handling utilities
- **cover_utils.py**: Album cover utilities

---

## 🔒 Security

- API keys and sensitive credentials are stored in `.env` file
- The `.env` file is excluded from version control
- OAuth authentication is used for Mixcloud integration
- HTTPS is used for all API communications

---

## 📞 Support

If you encounter any issues or have questions:

1. Check the [GitHub Issues](https://github.com/Katazui/DJAutomation/issues)
2. Create a new issue if your problem isn't already reported

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Stay tuned for more features and improvements! Thank you for using DJ Automation CLI. 🎉
