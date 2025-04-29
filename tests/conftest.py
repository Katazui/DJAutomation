"""
tests/conftest.py

Global pytest fixtures and configuration for DJ Automation tests.
"""

import os
import sys
import pytest
from unittest.mock import patch
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Skip collecting interactive tests in CI environment
def pytest_configure(config):
    # Register custom markers
    config.addinivalue_line("markers", "interactive: mark test as requiring user input")
    config.addinivalue_line("markers", "slow: mark test as slow")
    
    # In CI environment, skip interactive tests
    if os.environ.get('CI') == 'true':
        setattr(config.option, 'markexpr', 'not interactive')

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the basic environment for tests, including directories and env vars."""
    # Create necessary directories if they don't exist
    test_dirs = [
        Path.home() / "Documents" / "DJCLI" / "configuration",
        Path.home() / "Documents" / "DJCLI" / "content" / "albumCovers" / "pexel",
        Path.home() / "Documents" / "DJCLI" / "content" / "download" / "download_music",
        Path.home() / "Documents" / "DJCLI" / "content" / "mixcloudContent",
    ]
    
    for directory in test_dirs:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Create dummy .env file if not exists
    env_file = Path(project_root) / ".env"
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write("MIXCLOUD_CLIENT_ID=test_id\n")
            f.write("MIXCLOUD_CLIENT_SECRET=test_secret\n")
            f.write("PEXEL_API_KEY=test_pexel_key\n")
    
    yield
    
    # Cleanup if needed
    # (leaving directories in place for now)

@pytest.fixture
def mock_input_values(request):
    """Mock user input with predetermined values."""
    with patch('builtins.input') as mock_input:
        mock_input.side_effect = request.param
        yield mock_input 