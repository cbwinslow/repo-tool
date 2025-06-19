import os
import logging
import keyring
import paramiko
import jwt
import secrets
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from typing import Optional, Dict, Any
from pathlib import Path
import ssl
import certifi
import yaml
import re

class SecurityManager:
    def __init__(self, app_name: str = "DeltaAudio"):
        self.app_name = app_name
        self._setup_logging()
        self.keyring = keyring.get_keyring()
        self._setup_ssh()
        self._setup_ssl()
        
    def _setup_logging(self):
        """Initialize logging with sensitive data masking"""
        self.logger = logging.getLogger(self.app_name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create rotating file handler
        log_file = log_dir / f"{self.app_name.lower()}_security.log"
        handler = logging.FileHandler(log_file)
        
        class SensitiveDataFilter(logging.Filter):
            def filter(self, record):
                # Mask sensitive patterns (tokens, keys, passwords)
                patterns = [
                    (r'token[:=]\s*[\'"]?\w+[\'"]?', 'token=***'),
                    (r'password[:=]\s*[\'"]?\w+[\'"]?', 'password=***'),
                    (r'key[:=]\s*[\'"]?[\w-]+[\'"]?', 'key=***'),
                    (r'ssh-\w+\s+\S+', 'ssh-key-***')
                ]
                for pattern, mask in patterns:
                    if hasattr(record, 'msg'):
                        record.msg = re.sub(pattern, mask, str(record.msg))
                return True
        
        handler.addFilter(SensitiveDataFilter())
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _setup_ssh(self):
        """Initialize SSH configuration"""
        self.ssh_dir = Path.home() / ".ssh"
        self.ssh_dir.mkdir(mode=0o700, exist_ok=True)
        
    def _setup_ssl(self):
        """Initialize SSL/TLS configuration"""
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        self.ssl_context.check_hostname = True

    def store_pat(self, service: str, token: str) -> bool:
        """Store Personal Access Token securely"""
        try:
            self.keyring.set_password(f"{self.app_name}_PAT", service, token)
            self.logger.info(f"Stored PAT for service: {service}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store PAT: {str(e)}")
            return False

    def get_pat(self, service: str) -> Optional[str]:
        """Retrieve Personal Access Token"""
        try:
            token = self.keyring.get_password(f"{self.app_name}_PAT", service)
            self.logger.info(f"Retrieved PAT for service: {service}")
            return token
        except Exception as e:
            self.logger.error(f"Failed to retrieve PAT: {str(e)}")
            return None

    def generate_ssh_key(self, name: str = "id_rsa") -> Optional[Dict[str, str]]:
        """Generate new SSH key pair"""
        try:
            key = paramiko.RSAKey.generate(2048)
            private_key_path = self.ssh_dir / name
            public_key_path = self.ssh_dir / f"{name}.pub"
            
            key.write_private_key_file(str(private_key_path))
            os.chmod(private_key_path, 0o600)
            
            with open(public_key_path, 'w') as f:
                f.write(f"{key.get_name()} {key.get_base64()}")
            os.chmod(public_key_path, 0o644)
            
            self.logger.info(f"Generated new SSH key pair: {name}")
            return {
                "private_key": str(private_key_path),
                "public_key": str(public_key_path)
            }
        except Exception as e:
            self.logger.error(f"Failed to generate SSH key: {str(e)}")
            return None

    def validate_connection(self, host: str, port: int) -> bool:
        """Validate connection security"""
        try:
            with ssl.create_connection((host, port)) as conn:
                with self.ssl_context.wrap_socket(conn, server_hostname=host) as ssl_conn:
                    cert = ssl_conn.getpeercert()
                    # Verify certificate is not expired
                    ssl.match_hostname(cert, host)
                    self.logger.info(f"Validated connection to {host}:{port}")
                    return True
        except Exception as e:
            self.logger.error(f"Connection validation failed: {str(e)}")
            return False

    def validate_repository(self, repo_url: str, expected_fingerprint: Optional[str] = None) -> bool:
        """Validate repository authenticity"""
        try:
            # Check if URL is HTTPS
            if not repo_url.startswith('https://'):
                self.logger.warning(f"Repository URL does not use HTTPS: {repo_url}")
                return False
            
            # Validate SSL certificate
            host = repo_url.split('/')[2]
            valid_conn = self.validate_connection(host, 443)
            
            if expected_fingerprint:
                # Validate repository fingerprint
                # Implementation depends on specific VCS system
                pass
                
            self.logger.info(f"Validated repository: {repo_url}")
            return valid_conn
        except Exception as e:
            self.logger.error(f"Repository validation failed: {str(e)}")
            return False

    def rotate_token(self, service: str, current_token: str) -> Optional[str]:
        """Implement token rotation"""
        try:
            # Generate new token (implementation depends on service API)
            new_token = secrets.token_urlsafe(32)
            
            # Store new token
            if self.store_pat(service, new_token):
                self.logger.info(f"Rotated token for service: {service}")
                return new_token
            return None
        except Exception as e:
            self.logger.error(f"Token rotation failed: {str(e)}")
            return None

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load security configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"Loaded security configuration from {config_path}")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            return {}

