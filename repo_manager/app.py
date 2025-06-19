from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Static, ListView
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.binding import Binding

class LoginScreen(Screen):
    """Login screen for repository credentials."""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("enter", "submit", "Submit"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Header(show_clock=True),
            Vertical(
                Static("Repository Manager Login", id="title"),
                Input(placeholder="GitHub Token", id="github_token", password=True),
                Input(placeholder="GitLab Token", id="gitlab_token", password=True),
                Input(placeholder="Bitbucket Username", id="bitbucket_username"),
                Input(placeholder="Bitbucket Token", id="bitbucket_token", password=True),
                Button("Login", variant="primary", id="login"),
                id="login_form"
            ),
            Footer()
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login":
            self.save_credentials()
    
    def save_credentials(self) -> None:
        """Save credentials to keyring."""
        from .core.credential_manager import CredentialManager
        cred_manager = CredentialManager()
        
        for field in ["github_token", "gitlab_token", "bitbucket_username", "bitbucket_token"]:
            value = self.query_one(f"#{field}").value
            if value:
                cred_manager.set_credential(field, value)
        
        self.app.push_screen("main")

class MainScreen(Screen):
    """Main application screen."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Header(show_clock=True),
            Horizontal(
                Vertical(
                    Static("Repositories", id="repo_list_title"),
                    ListView(id="repo_list"),
                    Button("Add Repository", variant="primary", id="add_repo"),
                    id="left_pane"
                ),
                Vertical(
                    Static("Repository Details", id="repo_details_title"),
                    Static("", id="repo_details"),
                    id="right_pane"
                ),
                id="main_container"
            ),
            Footer()
        )

    def on_mount(self) -> None:
        """Load repositories when the screen is mounted."""
        self.load_repositories()
    
    def load_repositories(self) -> None:
        """Load repositories from all configured platforms."""
        from .core.repo_handler import RepositoryHandler
        from .core.credential_manager import CredentialManager
        
        cred_manager = CredentialManager()
        repo_handler = RepositoryHandler(cred_manager)
        
        # TODO: Implement repository loading
        pass

class RepoManagerApp(App):
    """Main repository manager application."""
    
    CSS = """
    Screen {
        align: center middle;
    }

    #login_form {
        width: 60;
        height: auto;
        border: solid green;
        padding: 1 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        padding: 1;
    }

    Input {
        margin: 1 0;
    }

    Button {
        margin: 1 0;
    }

    #main_container {
        width: 100%;
        height: 100%;
    }

    #left_pane {
        width: 30%;
        min-width: 20;
        border: solid green;
    }

    #right_pane {
        width: 70%;
        border: solid green;
    }
    """

    SCREENS = {
        "login": LoginScreen,
        "main": MainScreen,
    }

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def on_mount(self) -> None:
        """Start with the login screen."""
        self.push_screen("login")

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark

