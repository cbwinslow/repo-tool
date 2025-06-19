"""
Tests for core functionality
"""
import pytest
from pathlib import Path
from repo_tool.core.config import Config
from repo_tool.core.auth import TokenManager
from repo_tool.core.repo import Repository, RepoManager

def test_config_creation(config):
    """Test configuration creation"""
    assert config.config_file.exists()
    assert config.get("theme") == "dark"
    assert isinstance(config.get_download_path(), Path)

def test_config_modification(config):
    """Test configuration modification"""
    config.set("theme", "light")
    assert config.get("theme") == "light"
    
    config.reset()
    assert config.get("theme") == "dark"

def test_token_management(token_manager):
    """Test token storage and retrieval"""
    test_token = "test_token_123"
    token_manager.store_token("github", test_token)
    assert token_manager.get_token("github") == test_token
    
    token_manager.clear_tokens()
    assert token_manager.get_token("github") is None

def test_repository_validation(temp_dir):
    """Test repository path validation"""
    repo_manager = RepoManager()
    
    # Test valid path
    assert repo_manager.validate_destination(temp_dir)
    
    # Test non-existent path
    invalid_path = temp_dir / "nonexistent" / "path"
    assert repo_manager.validate_destination(invalid_path)

def test_repository_download(temp_dir, monkeypatch):
    """Test repository download functionality"""
    repo = Repository(
        name="test-repo",
        service="github",
        url="https://github.com/test/test-repo.git"
    )
    
    # Mock git.Repo.clone_from to avoid actual cloning
    def mock_clone_from(*args, **kwargs):
        (temp_dir / repo.name).mkdir()
    
    monkeypatch.setattr("git.Repo.clone_from", mock_clone_from)
    
    repo_manager = RepoManager()
    repo_manager.download_repository(repo, temp_dir)
    
    assert (temp_dir / repo.name).exists()

def test_download_to_existing_directory(temp_dir):
    """Test downloading to an existing directory"""
    repo = Repository(
        name="test-repo",
        service="github",
        url="https://github.com/test/test-repo.git"
    )
    
    # Create directory that would conflict with repository
    (temp_dir / repo.name).mkdir()
    
    repo_manager = RepoManager()
    with pytest.raises(ValueError):
        repo_manager.download_repository(repo, temp_dir)

