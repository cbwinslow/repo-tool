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
    """
    Creates and returns a `Config` instance with its configuration directory and file set up in a temporary location for testing.
    
    Parameters:
        temp_dir (Path): Temporary directory used as the base for the configuration paths.
    
    Returns:
        Config: A `Config` object initialized with default configuration in the temporary directory.
    """
    config = Config()
    config.config_dir = temp_dir / ".config" / "repo_tool"
    config.config_file = config.config_dir / "config.yaml"
    config._create_default_config()
    return config

@pytest.fixture
def token_manager(temp_dir):
    """
    Create a TokenManager instance for testing with an in-memory keyring backend.
    
    All keyring operations are redirected to an internal dictionary, ensuring test isolation from external keyring services. The keyring namespace is set to "repo_tool_test" for test-specific separation.
    
    Parameters:
        temp_dir (Path): Temporary directory fixture used for test isolation.
    
    Returns:
        TokenManager: A TokenManager instance configured to use the in-memory keyring.
    """
    tm = TokenManager()
    tm.KEYRING_NAMESPACE = "repo_tool_test"
    storage = {}

    def set_password(service, username, password):
        """
        Store a password in the in-memory storage for the given service and username.
        
        Parameters:
            service (str): The service identifier.
            username (str): The username associated with the password.
            password (str): The password to store.
        """
        storage[(service, username)] = password

    def get_password(service, username):
        """
        Retrieve a stored password for the given service and username from the in-memory storage.
        
        Parameters:
            service (str): The name of the service.
            username (str): The username associated with the password.
        
        Returns:
            str or None: The stored password if found, otherwise None.
        """
        return storage.get((service, username))

    def delete_password(service, username):
        """
        Remove the password entry for the specified service and username from the in-memory storage.
        """
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

