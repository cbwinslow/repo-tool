"""
Test configuration and fixtures
"""
import pytest
from pathlib import Path
import tempfile
import shutil
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

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
    config._create_default_config()
    return config

@pytest.fixture
def token_manager(temp_dir):
    """Create a test token manager"""
    tm = TokenManager()
    tm.KEYRING_NAMESPACE = "repo_tool_test"
    storage = {}

    def set_password(service, username, password):
        storage[(service, username)] = password

    def get_password(service, username):
        return storage.get((service, username))

    def delete_password(service, username):
        storage.pop((service, username), None)

    tm._keyring = {
        "set_password": set_password,
        "get_password": get_password,
        "delete_password": delete_password,
    }

    import keyring
    keyring.set_password = set_password
    keyring.get_password = get_password
    keyring.delete_password = delete_password

    return tm

