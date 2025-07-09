"""
Configuration management for RepoTool
"""
from pathlib import Path
import yaml
from typing import Dict, Any, Optional
import os

import os
import subprocess
import getpass

def get_git_config(key: str) -> str:
    """Get git configuration value"""
    try:
        result = subprocess.run(
            ["git", "config", "--global", key],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return ""

# Get system username and git configuration
USERNAME = getpass.getuser()
GIT_EMAIL = get_git_config("user.email") or ""
GIT_USERNAME = get_git_config("user.name") or USERNAME

DEFAULT_CONFIG = {
    "user": {
        "name": GIT_USERNAME,
        "email": GIT_EMAIL,
        "home_dir": str(Path.home())
    },
    "paths": {
        "default_download": str(Path.home() / "repositories"),
        "temp": str(Path.home() / ".cache" / "repo_tool"),
        "logs": str(Path.home() / ".local" / "share" / "repo_tool" / "logs")
    },
    "display": {
        "theme": "dark",
        "show_progress": True,
        "show_messages": True,
        "message_retention_days": 7
    },
    "updates": {
        "auto_check": True,
        "check_interval_days": 7,
        "last_check": None
    },
    "download": {
        "max_concurrent": 3,
        "timeout_seconds": 300,
        "verify_ssl": True,
        "allow_multiple_selection": True
    },
    "services": {
        "github": {
            "enabled": True,
            "use_gh_cli": True,
            "prefer_ssh": True
        },
        "gitlab": {
            "enabled": True,
            "prefer_ssh": True
        },
        "bitbucket": {
            "enabled": True,
            "prefer_ssh": True
        }
    }
}

class Config:
    """Manages application configuration"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "repo_tool"
        self.config_file = self.config_dir / "config.yaml"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if not self.config_file.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_file) as f:
                config = yaml.safe_load(f)
            return {**DEFAULT_CONFIG, **config}  # Merge with defaults
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f)
        
        return DEFAULT_CONFIG.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value by key, with special handling for the "theme" key.
        
        If the key is "theme", the method looks for it within the "display" section of the configuration. Returns the provided default value if the key is not found.
        """
        if key in self.config:
            return self.config.get(key, default)
        if key == "theme":
            return self.config.get("display", {}).get("theme", default)
        return default

    def set(self, key: str, value: Any) -> None:
        """
        Sets a configuration value for the specified key.
        
        If the key is "theme", updates the "theme" value within the "display" section of the configuration. For all other keys, sets the value at the top level of the configuration dictionary. The updated configuration is saved to disk.
        """
        if key == "theme":
            self.config.setdefault("display", {})["theme"] = value
        else:
            self.config[key] = value
        self._save_config()

    def _save_config(self) -> None:
        """
        Writes the current configuration dictionary to the YAML configuration file.
        """
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f)

    def reset(self) -> None:
        """Reset configuration to defaults"""
        self.config = DEFAULT_CONFIG.copy()
        self._save_config()

    def get_download_path(self) -> Path:
        """Get configured download path
        
        Returns:
            Path: The configured download path, creating it if it doesn't exist
        """
        path = Path(self.get("paths", {}).get("default_download", str(Path.home() / "repositories")))
        path.mkdir(parents=True, exist_ok=True)
        return path
        
    def get_user_info(self) -> dict:
        """Get user information
        
        Returns:
            dict: Dictionary containing user name, email, and home directory
        """
        return self.get("user", {})
        
    def get_download_options(self) -> dict:
        """Get download configuration options
        
        Returns:
            dict: Dictionary containing download settings like concurrent downloads,
                  timeout, SSL verification, etc.
        """
        return self.get("download", {})
        
    def get_display_options(self) -> dict:
        """Get display configuration options
        
        Returns:
            dict: Dictionary containing display settings like theme,
                  progress bars, message center options
        """
        return self.get("display", {})
        
    def should_check_updates(self) -> bool:
        """Check if it's time to check for updates
        
        Returns:
            bool: True if updates should be checked, False otherwise
        """
        updates = self.get("updates", {})
        if not updates.get("auto_check", True):
            return False
            
        last_check = updates.get("last_check")
        interval = updates.get("check_interval_days", 7)
        
        if not last_check:
            return True
            
        from datetime import datetime, timedelta
        last_check_date = datetime.fromisoformat(last_check)
        return datetime.now() - last_check_date > timedelta(days=interval)
        
    def update_last_check(self) -> None:
        """Update the last update check timestamp"""
        from datetime import datetime
        self.config["updates"]["last_check"] = datetime.now().isoformat()
        self._save_config()

    def is_service_enabled(self, service: str) -> bool:
        """Check if a service is enabled"""
        return self.config.get("services", {}).get(service, {}).get("enabled", False)

