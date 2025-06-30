"""
Repository management functionality
"""
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
import os
import git
from github import Github
import gitlab
from atlassian import Bitbucket
from ..core.auth import TokenManager
from ..core.logger import get_logger
from .git_progress import ProgressReporter

logger = get_logger(__name__)

@dataclass
class Repository:
    name: str
    service: str
    url: str
    description: Optional[str] = None
    default_branch: str = "main"

class RepoManager:
    """Manages repository operations across different services"""
    
    def __init__(self):
        self.token_manager = TokenManager()
        self._setup_clients()

    def _setup_clients(self):
        """Initialize API clients for each service"""
        self.clients = {}
        
        # GitHub setup
        gh_token = self.token_manager.get_token("github")
        if gh_token:
            self.clients["github"] = Github(gh_token)
            
        # GitLab setup
        gl_token = self.token_manager.get_token("gitlab")
        if gl_token:
            self.clients["gitlab"] = gitlab.Gitlab(
                url='https://gitlab.com',
                private_token=gl_token
            )
            
        # Bitbucket setup
        bb_token = self.token_manager.get_token("bitbucket")
        if bb_token:
            self.clients["bitbucket"] = Bitbucket(
                url='https://api.bitbucket.org',
                token=bb_token
            )

    def get_all_repositories(self) -> List[Repository]:
        """Get repositories from all configured services"""
        repos = []
        
        for service, client in self.clients.items():
            try:
                if service == "github":
                    user_repos = client.get_user().get_repos()
                    repos.extend([
                        Repository(
                            name=repo.name,
                            service="github",
                            url=repo.clone_url,
                            description=repo.description,
                            default_branch=repo.default_branch
                        )
                        for repo in user_repos
                    ])
                elif service == "gitlab":
                    user_repos = client.projects.list(owned=True)
                    repos.extend([
                        Repository(
                            name=repo.name,
                            service="gitlab",
                            url=repo.http_url_to_repo,
                            description=repo.description,
                            default_branch=repo.default_branch
                        )
                        for repo in user_repos
                    ])
                elif service == "bitbucket":
                    user_repos = client.get_user_repos()
                    repos.extend([
                        Repository(
                            name=repo["name"],
                            service="bitbucket",
                            url=repo["links"]["clone"][0]["href"],
                            description=repo.get("description", ""),
                            default_branch=repo.get("mainbranch", {}).get("name", "main")
                        )
                        for repo in user_repos
                    ])
            except Exception as e:
                logger.error(f"Failed to fetch repositories from {service}: {e}")
                
        return repos

    def download_repository(
        self,
        repo: Repository,
        destination: Path,
        progress_callback=None
    ) -> None:
        """
        Clones the specified repository into the given destination directory.
        
        Parameters:
        	repo (Repository): The repository to be downloaded.
        	destination (Path): The directory where the repository will be cloned.
        	progress_callback (callable, optional): A callback function to report cloning progress.
        
        Raises:
        	ValueError: If the target repository directory already exists.
        	Exception: If cloning fails for any other reason.
        """
        try:
            # Ensure destination exists
            destination.mkdir(parents=True, exist_ok=True)
            
            # Determine full path
            repo_path = destination / repo.name
            
            # Check if repo already exists
            if repo_path.exists():
                raise ValueError(f"Repository directory already exists: {repo_path}")
            
            # Clone with progress
            progress = ProgressReporter(progress_callback)
            git.Repo.clone_from(
                repo.url,
                str(repo_path),
                progress=progress
            )
            
        except Exception as e:
            logger.error(f"Failed to download repository {repo.name}: {e}")
            raise

    def validate_destination(self, path: Path) -> bool:
        """Validate if a destination path is suitable for download"""
        try:
            # Check if path exists or can be created
            if not path.exists():
                path.mkdir(parents=True)
                path.rmdir()  # Clean up test directory
            
            # Check if path is writable
            return os.access(path.parent, os.W_OK)
        except Exception:
            return False

