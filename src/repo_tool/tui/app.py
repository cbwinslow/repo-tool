"""
RepoTool TUI Application
"""
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, ListView, Input, ProgressBar, Label, LoadingIndicator
from textual.screen import Screen
from textual.reactive import reactive
from textual.binding import Binding
from rich.text import Text

from ..core.auth import TokenManager
from ..core.repo import RepoManager
from ..core.config import Config
from pathlib import Path
import threading
from ..core.logger import setup_logger
from .repo_screen import RepoManagementScreen

# ASCII art logo
LOGO = """
██████╗ ███████╗██████╗  ██████╗ ████████╗ ██████╗  ██████╗ ██╗     
██╔══██╗██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║     
██████╔╝█████╗  ██████╔╝██║   ██║   ██║   ██║   ██║██║   ██║██║     
██╔══██╗██╔══╝  ██╔═══╝ ██║   ██║   ██║   ██║   ██║██║   ██║██║     
██║  ██║███████╗██║     ╚██████╔╝   ██║   ╚██████╔╝╚██████╔╝███████╗
╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝    ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
"""

class RepoToolApp(App):
    """Main RepoTool TUI Application"""
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("h", "help", "Help", show=True),
        Binding("s", "settings", "Settings", show=True),
        Binding("c", "cancel", "Cancel Download", show=False),
        Binding("m", "manage", "Manage Repositories", show=True),
    ]

    current_repo = reactive("")
    download_progress = reactive(0.0)
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.token_manager = TokenManager()
        self.repo_manager = RepoManager()
        self.logger = setup_logger()

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header(show_clock=True)
        yield Container(
            Label(LOGO, id="logo"),
            Vertical(
                Input(placeholder="Search repositories...", id="search"),
                ListView(id="repo-list"),
                ProgressBar(id="progress", show_percentage=True),
                Label("", id="status"),
            ),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Handle app mount"""
        self.check_auth()
        self.load_repositories()

    def check_auth(self) -> None:
        """Verify authentication tokens"""
        if not self.token_manager.has_valid_tokens():
            self.push_screen(AuthScreen())

    def load_repositories(self) -> None:
        """Load repositories from all configured services"""
        try:
            repos = self.repo_manager.get_all_repositories()
            self.repo_map = {repo.name: repo for repo in repos}
            self.query_one("#repo-list").clear()
            for repo in repos:
                self.query_one("#repo-list").append(repo.name)
        except Exception as e:
            self.logger.error(f"Failed to load repositories: {e}")
            self.notify(f"Error: {str(e)}", severity="error")

    def action_refresh(self) -> None:
        """Refresh repository list"""
        self.load_repositories()

    def action_help(self) -> None:
        """Show help screen"""
        self.push_screen(HelpScreen())

    def action_settings(self) -> None:
        """Show settings screen"""
        self.push_screen(SettingsScreen())
        
    def action_manage(self) -> None:
        """Show repository management screen"""
        self.push_screen(RepoManagementScreen())

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle repository selection"""
        self.current_repo = self.repo_map.get(event.item)
        if self.current_repo:
            self.push_screen(DownloadScreen(self.current_repo))

class AuthScreen(Screen):
    """Authentication Screen"""
    
    def compose(self) -> ComposeResult:
        yield Container(
            Label("Authentication Required"),
            Input(placeholder="GitHub PAT", id="github-pat", password=True),
            Input(placeholder="GitLab PAT", id="gitlab-pat", password=True),
            Input(placeholder="Bitbucket PAT", id="bitbucket-pat", password=True),
        )

class HelpScreen(Screen):
    """Help Screen"""
    
    def compose(self) -> ComposeResult:
        yield Container(
            Label("RepoTool Help"),
            Label("Keyboard Shortcuts:"),
            Label("q - Quit"),
            Label("r - Refresh repositories"),
            Label("h - Show this help"),
            Label("s - Open settings"),
            Label("c - Cancel download (when active)"),
        )

class SettingsScreen(Screen):
    """Settings Screen"""
    
    def compose(self) -> ComposeResult:
        yield Container(
            Label("Settings"),
            Input(placeholder="Default download location", id="download-path"),
            Label("Theme:"),
            ListView(["Light", "Dark", "System"], id="theme-list"),
        )

class DownloadScreen(Screen):
    """Download Screen"""

    def __init__(self, repo):
        super().__init__()
        self.repo = repo

    def compose(self) -> ComposeResult:
        yield Container(
            Label(f"Downloading {self.repo.name}", id="repo-label"),
            Input(placeholder="Download location", id="location"),
            LoadingIndicator(id="spinner"),
            ProgressBar(id="download-progress"),
            Label("", id="download-status"),
        )

    def on_mount(self) -> None:
        self.query_one("#spinner").display = True
        dest = self.query_one("#location").value or str(self.app.config.get_download_path())
        thread = threading.Thread(target=self._download, args=(Path(dest),), daemon=True)
        thread.start()

    def _download(self, dest: Path):
        self.app.repo_manager.download_repository(
            self.repo,
            dest,
            progress_callback=self.update_progress,
        )
        self.app.call_from_thread(self._finish)

    def _finish(self):
        self.query_one("#spinner").display = False
        self.query_one("#download-status").update("Download complete")

    def update_progress(self, percent: float, message: str):
        def _update():
            bar = self.query_one("#download-progress")
            bar.update(progress=percent)
            self.query_one("#download-status").update(f"{percent:.1f}% {message}")
        self.app.call_from_thread(_update)

