"""
Settings screen for the RepoTool TUI
"""
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import (
    Button,
    Input,
    Label,
    Switch,
    Select,
    RadioSet,
    RadioButton,
    Tabs,
    Tab,
    Pretty
)
from textual.binding import Binding
from pathlib import Path
from ..core.config import Config
from ..core.auth import TokenManager

class SettingsScreen(Screen):
    """Settings configuration screen"""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("ctrl+s", "save", "Save Settings"),
    ]

    def __init__(self):
        """
        Initialize the settings screen with configuration and credential management.
        
        Creates instances of the configuration manager and token manager for handling application settings and secure credential storage.
        """
        super().__init__()
        self.config = Config()
        self.token_manager = TokenManager()

    def compose(self) -> ComposeResult:
        """
        Constructs and yields the complete widget layout for the settings screen, including tabs for each settings category and their associated input fields.
        
        Returns:
            ComposeResult: An iterable of UI containers and widgets representing all settings categories, including General, User, Display, Downloads, Services, Credentials, and Updates, as well as action buttons for saving, resetting, and navigating back.
        """
        yield Container(
            Label("Settings", id="title"),
            Tabs(
                Tab("General", id="general"),
                Tab("User", id="user"),
                Tab("Display", id="display"),
                Tab("Downloads", id="downloads"),
                Tab("Services", id="services"),
                Tab("Credentials", id="credentials"),
                Tab("Updates", id="updates"),
            ),
            ScrollableContainer(
                # General Settings
                Container(
                    Vertical(
                        Label("Default Download Path:"),
                        Input(
                            placeholder="Default path for repository downloads",
                            id="default-download-path"
                        ),
                        Label("Temporary Files Path:"),
                        Input(
                            placeholder="Path for temporary files",
                            id="temp-path"
                        ),
                        Label("Log Files Path:"),
                        Input(
                            placeholder="Path for log files",
                            id="log-path"
                        ),
                    ),
                    id="general-settings",
                ),
                # User Settings
                Container(
                    Vertical(
                        Label("User Name:"),
                        Input(
                            placeholder="Your name",
                            id="user-name"
                        ),
                        Label("Email:"),
                        Input(
                            placeholder="Your email",
                            id="user-email"
                        ),
                    ),
                    id="user-settings",
                    classes="hidden"
                ),
                # Display Settings
                Container(
                    Vertical(
                        Label("Theme:"),
                        RadioSet(
                            RadioButton("Light", id="theme-light"),
                            RadioButton("Dark", id="theme-dark"),
                            RadioButton("System", id="theme-system"),
                            id="theme-select"
                        ),
                        Switch("Show Progress Bars", id="show-progress"),
                        Switch("Show Message Center", id="show-messages"),
                        Label("Message Retention (days):"),
                        Input(
                            placeholder="Days to keep messages",
                            id="message-retention"
                        ),
                    ),
                    id="display-settings",
                    classes="hidden"
                ),
                # Download Settings
                Container(
                    Vertical(
                        Label("Maximum Concurrent Downloads:"),
                        Input(
                            placeholder="Number of concurrent downloads",
                            id="max-concurrent"
                        ),
                        Label("Download Timeout (seconds):"),
                        Input(
                            placeholder="Download timeout in seconds",
                            id="download-timeout"
                        ),
                        Switch("Verify SSL Certificates", id="verify-ssl"),
                        Switch("Allow Multiple Selection", id="allow-multiple"),
                    ),
                    id="download-settings",
                    classes="hidden"
                ),
                # Services Settings
                Container(
                    Vertical(
                        Label("GitHub Settings:"),
                        Switch("Enable GitHub", id="github-enabled"),
                        Switch("Use GitHub CLI", id="github-cli"),
                        Switch("Prefer SSH for GitHub", id="github-ssh"),
                        Label("GitLab Settings:"),
                        Switch("Enable GitLab", id="gitlab-enabled"),
                        Switch("Prefer SSH for GitLab", id="gitlab-ssh"),
                        Label("Bitbucket Settings:"),
                        Switch("Enable Bitbucket", id="bitbucket-enabled"),
                        Switch("Prefer SSH for Bitbucket", id="bitbucket-ssh"),
                    ),
                    id="services-settings",
                    classes="hidden"
                ),
                # Credentials Settings
                Container(
                    Vertical(
                        Label("GitHub Token:"),
                        Input(placeholder="GitHub PAT", id="github-token", password=True),
                        Label("GitLab Token:"),
                        Input(placeholder="GitLab PAT", id="gitlab-token", password=True),
                        Label("Bitbucket Username:"),
                        Input(placeholder="Username", id="bitbucket-user"),
                        Label("Bitbucket App Password:"),
                        Input(placeholder="App password", id="bitbucket-token", password=True),
                    ),
                    id="credentials-settings",
                    classes="hidden"
                ),
                # Update Settings
                Container(
                    Vertical(
                        Switch("Automatically Check for Updates", id="auto-update"),
                        Label("Check Interval (days):"),
                        Input(
                            placeholder="Days between update checks",
                            id="update-interval"
                        ),
                        Button("Check for Updates Now", variant="primary", id="check-updates"),
                        Label("Last Check:", id="last-check"),
                    ),
                    id="update-settings",
                    classes="hidden"
                ),
            ),
            Horizontal(
                Button("Save", variant="primary", id="save"),
                Button("Reset to Defaults", variant="default", id="reset"),
                Button("Back", variant="default", id="back"),
            ),
        )

    def on_mount(self) -> None:
        """Load current settings when the screen is mounted"""
        self.load_settings()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle tab changes"""
        # Hide all settings containers
        for container in self.query("Container.hidden, Container:not(.hidden)"):
            container.add_class("hidden")

        # Show the selected container
        settings_id = f"{event.tab.id}-settings"
        container = self.query_one(f"#{settings_id}")
        container.remove_class("hidden")

    def load_settings(self) -> None:
        """
        Populate the settings UI with current configuration values and stored credentials.
        
        Loads configuration data for paths, user information, display, download, services, and update settings from the application's configuration object, and fills the corresponding UI widgets. Also retrieves and displays stored authentication credentials for GitHub, GitLab, and Bitbucket using the token manager.
        """
        # Load paths
        paths = self.config.get("paths", {})
        self.query_one("#default-download-path").value = paths.get("default_download", "")
        self.query_one("#temp-path").value = paths.get("temp", "")
        self.query_one("#log-path").value = paths.get("logs", "")

        # Load user info
        user = self.config.get("user", {})
        self.query_one("#user-name").value = user.get("name", "")
        self.query_one("#user-email").value = user.get("email", "")

        # Load display settings
        display = self.config.get("display", {})
        theme = display.get("theme", "dark")
        self.query_one(f"#theme-{theme}").value = True
        self.query_one("#show-progress").value = display.get("show_progress", True)
        self.query_one("#show-messages").value = display.get("show_messages", True)
        self.query_one("#message-retention").value = str(display.get("message_retention_days", 7))

        # Load download settings
        download = self.config.get("download", {})
        self.query_one("#max-concurrent").value = str(download.get("max_concurrent", 3))
        self.query_one("#download-timeout").value = str(download.get("timeout_seconds", 300))
        self.query_one("#verify-ssl").value = download.get("verify_ssl", True)
        self.query_one("#allow-multiple").value = download.get("allow_multiple_selection", True)

        # Load service settings
        services = self.config.get("services", {})
        for service in ["github", "gitlab", "bitbucket"]:
            service_config = services.get(service, {})
            self.query_one(f"#{service}-enabled").value = service_config.get("enabled", True)
            if service == "github":
                self.query_one("#github-cli").value = service_config.get("use_gh_cli", True)
            self.query_one(f"#{service}-ssh").value = service_config.get("prefer_ssh", True)

        # Load update settings
        updates = self.config.get("updates", {})
        self.query_one("#auto-update").value = updates.get("auto_check", True)
        self.query_one("#update-interval").value = str(updates.get("check_interval_days", 7))
        last_check = updates.get("last_check", "Never")
        self.query_one("#last-check").update(f"Last Check: {last_check}")

        # Load stored credentials
        self.query_one("#github-token").value = self.token_manager.get_token("github") or ""
        self.query_one("#gitlab-token").value = self.token_manager.get_token("gitlab") or ""
        self.query_one("#bitbucket-user").value = self.token_manager.get_token("bitbucket_user") or ""
        self.query_one("#bitbucket-token").value = self.token_manager.get_token("bitbucket_token") or ""

    def save_settings(self) -> None:
        """
        Save the current configuration and credentials from the UI to persistent storage.
        
        Updates the application's configuration with values from the settings UI, including paths, user information, display preferences, download options, service settings, update preferences, and authentication credentials for supported services. Credentials are securely stored using the TokenManager. Persists all changes and notifies the user upon successful save.
        """
        # Save paths
        self.config.config["paths"] = {
            "default_download": self.query_one("#default-download-path").value,
            "temp": self.query_one("#temp-path").value,
            "logs": self.query_one("#log-path").value
        }

        # Save user info
        self.config.config["user"] = {
            "name": self.query_one("#user-name").value,
            "email": self.query_one("#user-email").value,
            "home_dir": str(Path.home())
        }

        # Save display settings
        theme = next(
            button.id.replace("theme-", "")
            for button in self.query("RadioButton")
            if button.value and button.id.startswith("theme-")
        )
        self.config.config["display"] = {
            "theme": theme,
            "show_progress": self.query_one("#show-progress").value,
            "show_messages": self.query_one("#show-messages").value,
            "message_retention_days": int(self.query_one("#message-retention").value or 7)
        }

        # Save download settings
        self.config.config["download"] = {
            "max_concurrent": int(self.query_one("#max-concurrent").value or 3),
            "timeout_seconds": int(self.query_one("#download-timeout").value or 300),
            "verify_ssl": self.query_one("#verify-ssl").value,
            "allow_multiple_selection": self.query_one("#allow-multiple").value
        }

        # Save service settings
        services = {}
        for service in ["github", "gitlab", "bitbucket"]:
            services[service] = {
                "enabled": self.query_one(f"#{service}-enabled").value,
                "prefer_ssh": self.query_one(f"#{service}-ssh").value
            }
            if service == "github":
                services[service]["use_gh_cli"] = self.query_one("#github-cli").value
        self.config.config["services"] = services

        # Save update settings
        self.config.config["updates"] = {
            "auto_check": self.query_one("#auto-update").value,
            "check_interval_days": int(self.query_one("#update-interval").value or 7),
            "last_check": self.config.get("updates", {}).get("last_check")
        }

        # Save credentials
        gt = self.query_one("#github-token").value
        if gt:
            self.token_manager.store_token("github", gt)
        glt = self.query_one("#gitlab-token").value
        if glt:
            self.token_manager.store_token("gitlab", glt)
        bu = self.query_one("#bitbucket-user").value
        if bu:
            self.token_manager.store_token("bitbucket_user", bu)
        btok = self.query_one("#bitbucket-token").value
        if btok:
            self.token_manager.store_token("bitbucket_token", btok)

        # Save all changes
        self.config._save_config()
        self.notify("Settings saved successfully!", severity="success")

    def action_save(self) -> None:
        """Save settings and notify user"""
        self.save_settings()

    def action_back(self) -> None:
        """Return to previous screen"""
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "save":
            self.save_settings()
        elif event.button.id == "reset":
            self.config.reset()
            self.load_settings()
            self.notify("Settings reset to defaults", severity="info")
        elif event.button.id == "back":
            self.dismiss()
        elif event.button.id == "check-updates":
            # This would be implemented in the updater module
            self.notify("Checking for updates...", severity="info")

