from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from github import Github
from gitlab import Gitlab
from atlassian import Bitbucket
from .credential_manager import CredentialManager

@dataclass
class Repository:
    """Represents a repository across different platforms."""
    name: str
    full_name: str
    description: str
    url: str
    platform: str
    private: bool
    default_branch: str
    stars: int = 0
    forks: int = 0

class RepositoryHandler:
    def __init__(self, cred_manager: CredentialManager):
        """Initialize repository handler."""
        self.cred_manager = cred_manager
        self._github: Optional[Github] = None
        self._gitlab: Optional[Gitlab] = None
        self._bitbucket: Optional[Bitbucket] = None

    def init_github(self) -> Optional[Github]:
        """Initialize GitHub client."""
        if not self.cred_manager.has_credentials("github"):
            return None
            
        token = self.cred_manager.get_credential("github_token")
        self._github = Github(token)
        return self._github

    def init_gitlab(self, url: str = "https://gitlab.com") -> Optional[Gitlab]:
        """Initialize GitLab client."""
        if not self.cred_manager.has_credentials("gitlab"):
            return None
            
        token = self.cred_manager.get_credential("gitlab_token")
        self._gitlab = Gitlab(url, private_token=token)
        return self._gitlab

    def init_bitbucket(self, url: str = "https://bitbucket.org") -> Optional[Bitbucket]:
        """Initialize Bitbucket client."""
        if not self.cred_manager.has_credentials("bitbucket"):
            return None
            
        username = self.cred_manager.get_credential("bitbucket_username")
        token = self.cred_manager.get_credential("bitbucket_token")
        self._bitbucket = Bitbucket(url=url, username=username, password=token)
        return self._bitbucket

    def list_github_repos(self) -> List[Repository]:
        """List GitHub repositories."""
        repos = []
        if not self._github:
            self.init_github()
        if self._github:
            for repo in self._github.get_user().get_repos():
                repos.append(Repository(
                    name=repo.name,
                    full_name=repo.full_name,
                    description=repo.description or "",
                    url=repo.html_url,
                    platform="github",
                    private=repo.private,
                    default_branch=repo.default_branch,
                    stars=repo.stargazers_count,
                    forks=repo.forks_count
                ))
        return repos

    def list_gitlab_repos(self) -> List[Repository]:
        """List GitLab repositories."""
        repos = []
        if not self._gitlab:
            self.init_gitlab()
        if self._gitlab:
            for project in self._gitlab.projects.list(owned=True):
                repos.append(Repository(
                    name=project.name,
                    full_name=project.path_with_namespace,
                    description=project.description or "",
                    url=project.web_url,
                    platform="gitlab",
                    private=not project.public,
                    default_branch=project.default_branch,
                    stars=project.star_count,
                    forks=project.forks_count
                ))
        return repos

    def list_bitbucket_repos(self) -> List[Repository]:
        """List Bitbucket repositories."""
        repos = []
        if not self._bitbucket:
            self.init_bitbucket()
        if self._bitbucket:
            # Note: Bitbucket API returns a dictionary
            for repo in self._bitbucket.repo_list():
                repos.append(Repository(
                    name=repo["name"],
                    full_name=f"{repo['owner']}/{repo['name']}",
                    description=repo.get("description", ""),
                    url=f"https://bitbucket.org/{repo['full_name']}",
                    platform="bitbucket",
                    private=not repo.get("is_private", True),
                    default_branch=repo.get("mainbranch", {}).get("name", "master"),
                    stars=0,  # Bitbucket doesn't have stars
                    forks=0   # Need additional API call for forks
                ))
        return repos

    def list_all_repos(self) -> List[Repository]:
        """List repositories from all configured platforms."""
        all_repos = []
        all_repos.extend(self.list_github_repos())
        all_repos.extend(self.list_gitlab_repos())
        all_repos.extend(self.list_bitbucket_repos())
        return all_repos

    def get_repo_details(self, platform: str, repo_path: str) -> Dict[str, Any]:
        """Get detailed information about a specific repository."""
        if platform == "github" and self._github:
            repo = self._github.get_repo(repo_path)
            return {
                "name": repo.name,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "open_issues": repo.open_issues_count,
                "default_branch": repo.default_branch,
                "language": repo.language,
                "created_at": repo.created_at,
                "updated_at": repo.updated_at,
                "clone_url": repo.clone_url,
            }
        elif platform == "gitlab" and self._gitlab:
            project = self._gitlab.projects.get(repo_path)
            return {
                "name": project.name,
                "description": project.description,
                "stars": project.star_count,
                "forks": project.forks_count,
                "open_issues": project.open_issues_count,
                "default_branch": project.default_branch,
                "created_at": project.created_at,
                "last_activity_at": project.last_activity_at,
                "clone_url": project.http_url_to_repo,
            }
        elif platform == "bitbucket" and self._bitbucket:
            owner, repo_name = repo_path.split("/")
            repo = self._bitbucket.get_repo(repo_path)
            return {
                "name": repo["name"],
                "description": repo.get("description", ""),
                "created_at": repo["created_on"],
                "updated_at": repo["updated_on"],
                "language": repo.get("language", ""),
                "clone_url": f"https://bitbucket.org/{repo_path}.git",
            }
        return {}

