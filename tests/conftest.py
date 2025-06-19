"""
Test configuration and fixtures
"""
import pytest
from pathlib import Path
import tempfile
import shutil
from repo_tool.core.config import Config
from repo_tool.core.auth import TokenManager

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def config(temp_dir):
    """Create a test configuration"""
    config = Config()
    config.config_dir = temp_dir / ".config" / "repo_tool"
    config.config_file = config.config_dir / "config.yaml"
    return config

@pytest.fixture
def token_manager(temp_dir):
    """Create a test token manager"""
    tm = TokenManager()
    # Override keyring for testing
    tm.KEYRING_NAMESPACE = "repo_tool_test"
    return tm

