"""
Advanced repository operations using gh CLI and API integrations
"""
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json
from github import Github
import gitlab
from atlassian import Bitbucket
from .logger import get_logger
from .auth import TokenManager

logger = get_logger(__name__)

@dataclass
class RepoCreateOptions:
    name: str
    description: Optional[str] = None
    private: bool = False
    team: Optional[str] = None
    template: Optional[str] = None
    license: Optional[str] = None
    gitignore: Optional[str] = None

@dataclass
class RepoInfo:
    name: str
    owner: str
    description: Optional[str]
    url: str
    is_private: bool
    default_branch: str
    stars: int
    forks: int
    service: str

class RepositoryOperations:
    """Advanced repository operations manager"""
    
    def __init__(self):
        self.token_manager = TokenManager()
        self._setup_clients()

    def _setup_clients(self):
        """Initialize API clients"""
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

    def create_repository(
        self,
        options: RepoCreateOptions,
        service: str = "github"
    ) -> RepoInfo:
        """Create a new repository"""
        try:
            if service == "github":
                return self._create_github_repository(options)
            elif service == "gitlab":
                return self._create_gitlab_repository(options)
            elif service == "bitbucket":
                return self._create_bitbucket_repository(options)
            else:
                raise ValueError(f"Unsupported service: {service}")
        except Exception as e:
            logger.error(f"Failed to create repository: {e}")
            raise

    def _create_github_repository(self, options: RepoCreateOptions) -> RepoInfo:
        """Create a GitHub repository using gh CLI"""
        cmd = ["gh", "repo", "create", options.name]
        
        if options.description:
            cmd.extend(["--description", options.description])
        
        if options.private:
            cmd.append("--private")
        else:
            cmd.append("--public")
            
        if options.template:
            cmd.extend(["--template", options.template])
            
        if options.license:
            cmd.extend(["--license", options.license])
            
        if options.gitignore:
            cmd.extend(["--gitignore", options.gitignore])
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get repository details using API
            gh_client = self.clients["github"]
            repo = gh_client.get_repo(f"{gh_client.get_user().login}/{options.name}")
            
            return RepoInfo(
                name=repo.name,
                owner=repo.owner.login,
                description=repo.description,
                url=repo.clone_url,
                is_private=repo.private,
                default_branch=repo.default_branch,
                stars=repo.stargazers_count,
                forks=repo.forks_count,
                service="github"
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"gh CLI error: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Failed to create GitHub repository: {e}")
            raise

    def fork_repository(
        self,
        repo_name: str,
        service: str = "github",
        org: Optional[str] = None
    ) -> RepoInfo:
        """Fork a repository"""
        try:
            if service == "github":
                return self._fork_github_repository(repo_name, org)
            elif service == "gitlab":
                return self._fork_gitlab_repository(repo_name, org)
            elif service == "bitbucket":
                return self._fork_bitbucket_repository(repo_name, org)
            else:
                raise ValueError(f"Unsupported service: {service}")
        except Exception as e:
            logger.error(f"Failed to fork repository: {e}")
            raise

    def _fork_github_repository(
        self,
        repo_name: str,
        org: Optional[str] = None
    ) -> RepoInfo:
        """Fork a GitHub repository using gh CLI"""
        cmd = ["gh", "repo", "fork", repo_name]
        
        if org:
            cmd.extend(["--org", org])
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Get forked repo details
            owner = org if org else self.clients["github"].get_user().login
            repo = self.clients["github"].get_repo(f"{owner}/{repo_name.split('/')[-1]}")
            
            return RepoInfo(
                name=repo.name,
                owner=repo.owner.login,
                description=repo.description,
                url=repo.clone_url,
                is_private=repo.private,
                default_branch=repo.default_branch,
                stars=repo.stargazers_count,
                forks=repo.forks_count,
                service="github"
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"gh CLI error: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Failed to fork GitHub repository: {e}")
            raise

    def delete_repository(
        self,
        repo_name: str,
        service: str = "github",
        confirm: bool = True
    ) -> bool:
        """Delete a repository"""
        try:
            if service == "github":
                return self._delete_github_repository(repo_name, confirm)
            elif service == "gitlab":
                return self._delete_gitlab_repository(repo_name, confirm)
            elif service == "bitbucket":
                return self._delete_bitbucket_repository(repo_name, confirm)
            else:
                raise ValueError(f"Unsupported service: {service}")
        except Exception as e:
            logger.error(f"Failed to delete repository: {e}")
            raise

    def _delete_github_repository(
        self,
        repo_name: str,
        confirm: bool = True
    ) -> bool:
        """Delete a GitHub repository using gh CLI"""
        cmd = ["gh", "repo", "delete", repo_name]
        
        if not confirm:
            cmd.append("--yes")
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"gh CLI error: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete GitHub repository: {e}")
            return False

    def create_issue(
        self,
        repo_name: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        service: str = "github"
    ) -> Dict[str, Any]:
        """Create an issue in a repository"""
        try:
            if service == "github":
                return self._create_github_issue(repo_name, title, body, labels, assignees)
            elif service == "gitlab":
                return self._create_gitlab_issue(repo_name, title, body, labels, assignees)
            elif service == "bitbucket":
                return self._create_bitbucket_issue(repo_name, title, body, labels, assignees)
            else:
                raise ValueError(f"Unsupported service: {service}")
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            raise

    def _create_github_issue(
        self,
        repo_name: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a GitHub issue using gh CLI"""
        cmd = ["gh", "issue", "create"]
        cmd.extend(["--title", title])
        cmd.extend(["--body", body])
        
        if labels:
            cmd.extend(["--label", ",".join(labels)])
            
        if assignees:
            cmd.extend(["--assignee", ",".join(assignees)])
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse URL from output and get issue details
            issue_url = result.stdout.strip()
            return {
                "url": issue_url,
                "title": title,
                "body": body,
                "labels": labels or [],
                "assignees": assignees or []
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"gh CLI error: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Failed to create GitHub issue: {e}")
            raise

    def search_repositories(
        self,
        query: str,
        service: str = "github",
        limit: int = 10
    ) -> List[RepoInfo]:
        """Search for repositories"""
        try:
            if service == "github":
                return self._search_github_repositories(query, limit)
            elif service == "gitlab":
                return self._search_gitlab_repositories(query, limit)
            elif service == "bitbucket":
                return self._search_bitbucket_repositories(query, limit)
            else:
                raise ValueError(f"Unsupported service: {service}")
        except Exception as e:
            logger.error(f"Failed to search repositories: {e}")
            raise

    def _search_github_repositories(
        self,
        query: str,
        limit: int = 10
    ) -> List[RepoInfo]:
        """Search GitHub repositories using gh CLI"""
        cmd = ["gh", "search", "repos", query, "--json", "nameWithOwner,description,url,isPrivate,defaultBranchRef,stargazerCount,forkCount"]
        cmd.extend(["--limit", str(limit)])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            repos_data = json.loads(result.stdout)
            return [
                RepoInfo(
                    name=repo["nameWithOwner"].split("/")[-1],
                    owner=repo["nameWithOwner"].split("/")[0],
                    description=repo.get("description"),
                    url=repo["url"],
                    is_private=repo["isPrivate"],
                    default_branch=repo["defaultBranchRef"]["name"],
                    stars=repo["stargazerCount"],
                    forks=repo["forkCount"],
                    service="github"
                )
                for repo in repos_data
            ]
        except subprocess.CalledProcessError as e:
            logger.error(f"gh CLI error: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Failed to search GitHub repositories: {e}")
            raise

