"""
Repository management screen for the TUI
"""
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Input,
    Label,
    Select,
    Switch,
    RadioSet,
    RadioButton,
    ListView,
    LoadingIndicator
)
from textual.binding import Binding
from textual.message import Message

from ..core.repo_ops import RepositoryOperations, RepoCreateOptions, RepoInfo

class CreateRepoDialog(Screen):
    """Dialog for creating a new repository"""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "submit", "Create Repository"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Create New Repository", id="title"),
            Input(placeholder="Repository name", id="name"),
            Input(placeholder="Description (optional)", id="description"),
            Switch("Private repository", id="private"),
            Select(
                ((lic, lic) for lic in [
                    "mit", "apache-2.0", "gpl-3.0",
                    "bsd-2-clause", "bsd-3-clause", "unlicense"
                ]),
                prompt="Choose a license",
                id="license"
            ),
            Select(
                ((gi, gi) for gi in [
                    "Python", "Node", "Go", "Rust",
                    "Java", "Ruby", "C++", "C"
                ]),
                prompt="Choose .gitignore template",
                id="gitignore"
            ),
            Horizontal(
                Button("Create", variant="primary", id="create"),
                Button("Cancel", variant="default", id="cancel"),
            ),
            id="create-dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "cancel":
            self.dismiss()
        elif event.button.id == "create":
            self.create_repository()

    def create_repository(self) -> None:
        """Create a new repository"""
        name = self.query_one("#name").value
        description = self.query_one("#description").value
        private = self.query_one("#private").value
        license = self.query_one("#license").value
        gitignore = self.query_one("#gitignore").value

        if not name:
            self.notify("Repository name is required", severity="error")
            return

        options = RepoCreateOptions(
            name=name,
            description=description or None,
            private=private,
            license=license,
            gitignore=gitignore
        )

        try:
            repo_ops = RepositoryOperations()
            repo = repo_ops.create_repository(options)
            self.notify(f"Repository {repo.name} created successfully!", severity="success")
            self.dismiss(repo)
        except Exception as e:
            self.notify(f"Failed to create repository: {str(e)}", severity="error")

class IssueDialog(Screen):
    """Dialog for creating a new issue"""

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Create New Issue", id="title"),
            Input(placeholder="Issue title", id="title-input"),
            Input(placeholder="Issue description", id="body-input", classes="text-area"),
            Input(placeholder="Labels (comma-separated)", id="labels"),
            Input(placeholder="Assignees (comma-separated)", id="assignees"),
            Horizontal(
                Button("Create", variant="primary", id="create"),
                Button("Cancel", variant="default", id="cancel"),
            ),
            id="issue-dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "cancel":
            self.dismiss()
        elif event.button.id == "create":
            self.create_issue()

    def create_issue(self) -> None:
        """Create a new issue"""
        title = self.query_one("#title-input").value
        body = self.query_one("#body-input").value
        labels = [l.strip() for l in self.query_one("#labels").value.split(",") if l.strip()]
        assignees = [a.strip() for a in self.query_one("#assignees").value.split(",") if a.strip()]

        if not title:
            self.notify("Issue title is required", severity="error")
            return

        try:
            repo_ops = RepositoryOperations()
            issue = repo_ops.create_issue(
                self.repo_name,  # Set when dialog is shown
                title,
                body,
                labels,
                assignees
            )
            self.notify("Issue created successfully!", severity="success")
            self.dismiss(issue)
        except Exception as e:
            self.notify(f"Failed to create issue: {str(e)}", severity="error")

class RepoManagementScreen(Screen):
    """Main repository management screen"""

    BINDINGS = [
        Binding("n", "new_repo", "New Repository"),
        Binding("f", "fork_repo", "Fork Repository"),
        Binding("i", "new_issue", "New Issue"),
        Binding("d", "delete_repo", "Delete Repository"),
        Binding("s", "search", "Search"),
        Binding("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Container(
            Label("Repository Management", id="title"),
            Horizontal(
                Input(placeholder="Search repositories...", id="search-input"),
                Button("Search", variant="primary", id="search-button"),
            ),
            RadioSet(
                RadioButton("GitHub", id="github"),
                RadioButton("GitLab", id="gitlab"),
                RadioButton("Bitbucket", id="bitbucket"),
                id="service-select"
            ),
            LoadingIndicator(id="loading"),
            ListView(id="repo-list"),
            Vertical(
                Label("Repository Details", id="details-title"),
                Label("", id="repo-details"),
                classes="details-panel"
            ),
            id="repo-management"
        )

    def on_mount(self) -> None:
        """Handle screen mount"""
        self.repo_ops = RepositoryOperations()
        self.load_repositories()

    def load_repositories(self) -> None:
        """Load repositories for selected service"""
        service = self.get_selected_service()
        loading = self.query_one("#loading")
        loading.visible = True

        try:
            repos = self.repo_ops.search_repositories("", service=service)
            self.query_one("#repo-list").clear()
            for repo in repos:
                self.query_one("#repo-list").append(f"{repo.owner}/{repo.name}")
        except Exception as e:
            self.notify(f"Failed to load repositories: {str(e)}", severity="error")
        finally:
            loading.visible = False

    def get_selected_service(self) -> str:
        """Get currently selected service"""
        for button in self.query_one("#service-select").query("RadioButton"):
            if button.value:
                return button.id
        return "github"  # Default to GitHub

    def action_new_repo(self) -> None:
        """Show create repository dialog"""
        self.push_screen(CreateRepoDialog())

    def action_fork_repo(self) -> None:
        """Fork selected repository"""
        selected = self.query_one("#repo-list").selected
        if not selected:
            self.notify("Select a repository to fork", severity="warning")
            return

        try:
            repo = self.repo_ops.fork_repository(selected)
            self.notify(f"Repository forked successfully: {repo.name}", severity="success")
            self.load_repositories()
        except Exception as e:
            self.notify(f"Failed to fork repository: {str(e)}", severity="error")

    def action_new_issue(self) -> None:
        """Show create issue dialog"""
        selected = self.query_one("#repo-list").selected
        if not selected:
            self.notify("Select a repository to create an issue", severity="warning")
            return

        dialog = IssueDialog()
        dialog.repo_name = selected
        self.push_screen(dialog)

    def action_delete_repo(self) -> None:
        """Delete selected repository"""
        selected = self.query_one("#repo-list").selected
        if not selected:
            self.notify("Select a repository to delete", severity="warning")
            return

        try:
            if self.repo_ops.delete_repository(selected):
                self.notify(f"Repository {selected} deleted successfully", severity="success")
                self.load_repositories()
            else:
                self.notify("Failed to delete repository", severity="error")
        except Exception as e:
            self.notify(f"Failed to delete repository: {str(e)}", severity="error")

    def action_search(self) -> None:
        """Search repositories"""
        query = self.query_one("#search-input").value
        service = self.get_selected_service()
        loading = self.query_one("#loading")
        loading.visible = True

        try:
            repos = self.repo_ops.search_repositories(query, service=service)
            self.query_one("#repo-list").clear()
            for repo in repos:
                self.query_one("#repo-list").append(f"{repo.owner}/{repo.name}")
        except Exception as e:
            self.notify(f"Search failed: {str(e)}", severity="error")
        finally:
            loading.visible = False

    def action_back(self) -> None:
        """Return to main screen"""
        self.dismiss()

