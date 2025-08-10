"""
About screen for RepoTool
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import (
    Button,
    Label,
    Markdown,
    Footer
)
from textual.binding import Binding
from importlib.metadata import version, metadata
from pathlib import Path
import sys
import platform

# ASCII art logo
LOGO = """
██████╗ ███████╗██████╗  ██████╗ ████████╗ ██████╗  ██████╗ ██╗     
██╔══██╗██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║     
██████╔╝█████╗  ██████╔╝██║   ██║   ██║   ██║   ██║██║   ██║██║     
██╔══██╗██╔══╝  ██╔═══╝ ██║   ██║   ██║   ██║   ██║██║   ██║██║     
██║  ██║███████╗██║     ╚██████╔╝   ██║   ╚██████╔╝╚██████╔╝███████╗
╚═╝  ╚═╝╚══════╝╚═╝      ╚═════╝    ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
"""

ABOUT_TEXT = """
# About RepoTool

A powerful Terminal User Interface (TUI) for managing repositories across multiple services.

## Version Information
- Version: {version}
- Python: {python_version}
- Platform: {platform}
- Dependencies: {dependencies}

## Features
- Repository management across multiple services
- Secure credential storage
- Progress tracking and notifications
- Comprehensive error handling
- Configurable settings
- Message center with analytics

## File Locations
- Config: {config_path}
- Logs: {log_path}
- Cache: {cache_path}

## Contributors
- Blaine Winslow <blaine.winslow@gmail.com>

## Links
- Documentation: https://github.com/cbwinslow/repo-tool/docs
- Source Code: https://github.com/cbwinslow/repo-tool
- Issue Tracker: https://github.com/cbwinslow/repo-tool/issues

## License
MIT License - see LICENSE file for details
"""

class AboutScreen(Screen):
    """About screen showing application information"""
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("c", "copy", "Copy System Info"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Container(
            Label(LOGO, id="logo"),
            ScrollableContainer(
                Markdown(self.get_about_text()),
                id="about-content"
            ),
            Horizontal(
                Button("Copy System Info", variant="default", id="copy-info"),
                Button("Check for Updates", variant="primary", id="check-updates"),
                Button("View License", variant="default", id="view-license"),
                Button("Back", variant="default", id="back"),
                classes="button-container"
            ),
            Footer()
        )
        
    def get_about_text(self) -> str:
        """Get formatted about text"""
        try:
            pkg_version = version("repo-tool")
        except:
            pkg_version = "development"
            
        python_version = sys.version.split()[0]
        platform_info = f"{platform.system()} {platform.release()}"
        
        try:
            pkg_metadata = metadata("repo-tool")
            dependencies = ", ".join(pkg_metadata.get_all("Requires-Dist") or [])
        except:
            dependencies = "development environment"
            
        config_path = Path.home() / ".config" / "repo_tool"
        log_path = Path.home() / ".local" / "share" / "repo_tool" / "logs"
        cache_path = Path.home() / ".cache" / "repo_tool"
        
        return ABOUT_TEXT.format(
            version=pkg_version,
            python_version=python_version,
            platform=platform_info,
            dependencies=dependencies,
            config_path=config_path,
            log_path=log_path,
            cache_path=cache_path
        )
        
    def action_back(self) -> None:
        """Return to previous screen"""
        self.dismiss()
        
    def action_copy(self) -> None:
        """Copy system information to clipboard"""
        try:
            import pyperclip
            pyperclip.copy(self.get_system_info())
            self.notify("System information copied to clipboard", severity="success")
        except ImportError:
            self.notify("pyperclip not installed - cannot copy to clipboard", severity="error")
            
    def get_system_info(self) -> str:
        """Get detailed system information"""
        info = [
            "RepoTool System Information",
            "========================",
            f"Version: {version('repo-tool')}",
            f"Python: {sys.version}",
            f"Platform: {platform.platform()}",
            f"Machine: {platform.machine()}",
            f"Processor: {platform.processor()}",
            f"System: {platform.system()} {platform.release()}",
            "",
            "Python Path:",
            sys.executable,
            "",
            "Environment:",
            f"LANG: {os.environ.get('LANG', 'Not set')}",
            f"TERM: {os.environ.get('TERM', 'Not set')}",
            f"SHELL: {os.environ.get('SHELL', 'Not set')}",
            "",
            "Dependencies:",
        ]
        
        try:
            pkg_metadata = metadata("repo-tool")
            for dep in (pkg_metadata.get_all("Requires-Dist") or []):
                info.append(f"- {dep}")
        except:
            info.append("Development environment")
            
        return "\n".join(info)
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back":
            self.dismiss()
        elif event.button.id == "copy-info":
            self.action_copy()
        elif event.button.id == "check-updates":
            # This would be implemented in the updater module
            self.notify("Checking for updates...", severity="info")
        elif event.button.id == "view-license":
            self.show_license()
            
    def show_license(self) -> None:
        """Show license text"""
        try:
            license_path = Path(__file__).parent.parent.parent / "LICENSE"
            with open(license_path) as f:
                license_text = f.read()

            from .text_screen import TextScreen
            self.app.push_screen(TextScreen("License", license_text))
        except Exception as e:
            self.notify(f"Failed to open license: {e}", severity="error")
