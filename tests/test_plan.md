# DJ Automation Test Plan

This document outlines test cases for each module to ensure core functionality works as expected.

## 1. Download Module Tests

### `test_downloader.py`

#### Unit Tests

- `test_url_validation`: Test URL validation for YouTube, SoundCloud and other sources
- `test_metadata_extraction`: Verify title, artist extraction from URLs
- `test_download_single_track`: Test downloading a single track with mocked responses
- `test_file_saving`: Verify tracks save to correct location with proper permissions
- `test_batch_download`: Test handling multiple downloads sequentially
- `test_error_handling`: Test handling for network errors, invalid URLs, rate limiting

#### Integration Tests

- `test_end_to_end_download`: Test full download process with a test URL
- `test_file_mode_integration`: Test reading links from a file
- `test_interactive_mode`: Test interactive input mode (with mocked input)

### `test_download_pexel.py`

- `test_pexel_api_connection`: Verify connection to Pexel API
- `test_search_functionality`: Test search with different queries
- `test_photo_download`: Verify photo downloading with mock responses
- `test_error_handling`: Test API errors, rate limits, network issues

## 2. Covers Module Tests

### `test_create_album_cover.py`

- `test_image_loading`: Test loading different image formats and sizes
- `test_image_cropping`: Verify proper image cropping
- `test_text_overlay`: Test text placement and scaling
- `test_font_loading`: Test handling of custom fonts
- `test_output_quality`: Verify output image quality and format
- `test_file_naming`: Test output filename generation
- `test_config_loading`: Test loading album cover configuration
- `test_error_handling`: Test handling corrupt images, missing files

## 3. Organize Module Tests

### `test_organize_files.py`

- `test_file_detection`: Test finding audio files in directories
- `test_directory_creation`: Verify creation of organized directories
- `test_file_moving`: Test moving files between directories
- `test_metadata_organization`: Test organizing by metadata (artist, album)
- `test_duplicate_handling`: Test handling duplicate files
- `test_requested_vs_all`: Test filtering between requested and all files
- `test_error_handling`: Test permissions issues, missing files

## 4. Mixcloud Module Tests

### `test_uploader.py`

- `test_authentication`: Test OAuth authentication flow
- `test_track_validation`: Verify track format validation
- `test_metadata_extraction`: Test extracting metadata from audio files
- `test_cover_art_addition`: Test attaching cover art to uploads
- `test_upload_process`: Test the upload process with mock responses
- `test_scheduling`: Verify scheduled publishing functionality
- `test_retry_mechanism`: Test retry logic for failed uploads
- `test_dry_run_mode`: Validate dry run functionality
- `test_error_handling`: Test API errors, network issues, rate limiting

## 5. Core Utilities Tests

### `test_file_utils.py`

- `test_file_existence_check`: Test file existence verification
- `test_directory_creation`: Test creating nested directories
- `test_file_copying`: Test file copy operations
- `test_file_moving`: Verify file move operations
- `test_file_deletion`: Test safe file deletion
- `test_path_normalization`: Verify path handling across platforms

### `test_metadata_utils.py`

- `test_metadata_extraction`: Test extracting metadata from audio files
- `test_metadata_writing`: Test writing metadata to files
- `test_format_conversion`: Test converting between metadata formats
- `test_error_handling`: Test corrupt files, missing metadata

### `test_color_utils.py`

- `test_color_output`: Verify color code generation
- `test_message_formatting`: Test message type formatting
- `test_terminal_compatibility`: Test fallback for terminals without color

## 6. CLI Tests

### `test_main_cli.py`

- `test_argument_parsing`: Test parsing different command arguments
- `test_command_dispatching`: Verify commands route to correct handlers
- `test_help_output`: Test help text generation
- `test_version_display`: Verify version information display
- `test_color_output`: Test colored output rendering

### `test_mixcloud_cli.py`

- `test_mixcloud_options`: Test Mixcloud-specific CLI options
- `test_init_settings`: Verify initialization of Mixcloud settings
- `test_dry_run_flag`: Test dry run mode through CLI
- `test_error_handling`: Test CLI error display

## Implementation Guide

1. Use pytest fixtures to set up test environments
2. Mock external services (APIs, file operations) where appropriate
3. Create small test files for testing without requiring actual downloads
4. Use temporary directories for file operation tests
5. Implement parameterized tests for testing multiple scenarios
6. Use coverage reports to ensure thorough testing

## Example Test Structure

```python
import pytest
from unittest.mock import patch, MagicMock
from modules.download.downloader import validate_url, download_track

def test_url_validation():
    # Valid URLs
    assert validate_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == True
    assert validate_url("https://soundcloud.com/artist/track") == True

    # Invalid URLs
    assert validate_url("not-a-url") == False
    assert validate_url("http://invalid-domain.xyz") == False

@patch("modules.download.downloader.download_from_youtube")
def test_download_track(mock_download):
    # Setup mock
    mock_download.return_value = "/path/to/downloaded/file.mp3"

    # Test
    result = download_track("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    # Assertions
    assert mock_download.called
    assert result == "/path/to/downloaded/file.mp3"
```

## Continuous Integration

Implement these tests in a CI pipeline to ensure:

1. All tests pass before merging
2. Code coverage remains high
3. Performance regressions are detected

This testing plan provides a comprehensive framework for ensuring your DJ Automation project remains robust and reliable.
