import keyring
from typing import Optional

class CredentialManager:
    def __init__(self, namespace: str = "repo_manager"):
        """Initialize credential manager."""
        self.namespace = namespace

    def set_credential(self, key: str, value: str) -> None:
        """Store a credential in the system keyring."""
        keyring.set_password(self.namespace, key, value)

    def get_credential(self, key: str) -> Optional[str]:
        """Retrieve a credential from the system keyring."""
        return keyring.get_password(self.namespace, key)

    def delete_credential(self, key: str) -> None:
        """Delete a credential from the system keyring."""
        try:
            keyring.delete_password(self.namespace, key)
        except keyring.errors.PasswordDeleteError:
            pass  # Credential didn't exist

    def has_credentials(self, platform: str) -> bool:
        """Check if credentials exist for a given platform."""
        if platform == "github":
            return bool(self.get_credential("github_token"))
        elif platform == "gitlab":
            return bool(self.get_credential("gitlab_token"))
        elif platform == "bitbucket":
            return bool(self.get_credential("bitbucket_username") and 
                      self.get_credential("bitbucket_token"))
        return False

