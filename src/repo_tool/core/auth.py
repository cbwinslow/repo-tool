"""
Authentication management for repository services
"""
import keyring
from typing import Optional
from dataclasses import dataclass

@dataclass
class ServiceToken:
    service: str
    token: str
    is_valid: bool = False

class TokenManager:
    """Manages authentication tokens for various services"""
    
    KEYRING_NAMESPACE = "repo_tool"
    
    def __init__(self):
        self.services = ["github", "gitlab", "bitbucket"]

    def store_token(self, service: str, token: str) -> None:
        """Store a service token securely"""
        keyring.set_password(self.KEYRING_NAMESPACE, service, token)

    def get_token(self, service: str) -> Optional[str]:
        """Retrieve a service token"""
        return keyring.get_password(self.KEYRING_NAMESPACE, service)

    def validate_token(self, service: str, token: str) -> bool:
        """Validate a service token"""
        # Implementation would vary by service
        if service == "github":
            from github import Github
            try:
                g = Github(token)
                g.get_user().login
                return True
            except:
                return False
        elif service == "gitlab":
            import gitlab
            try:
                gl = gitlab.Gitlab(url='https://gitlab.com', private_token=token)
                gl.auth()
                return True
            except:
                return False
        elif service == "bitbucket":
            from atlassian import Bitbucket
            try:
                bb = Bitbucket(
                    url='https://api.bitbucket.org',
                    token=token
                )
                bb.get_user()
                return True
            except:
                return False
        return False

    def has_valid_tokens(self) -> bool:
        """Check if we have valid tokens for any service"""
        return any(
            self.get_token(service) is not None
            for service in self.services
        )

    def clear_tokens(self) -> None:
        """Clear all stored tokens"""
        for service in self.services:
            keyring.delete_password(self.KEYRING_NAMESPACE, service)

    def remove_token(self, service: str) -> None:
        """Remove a specific token"""
        keyring.delete_password(self.KEYRING_NAMESPACE, service)

