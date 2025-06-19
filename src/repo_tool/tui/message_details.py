"""
Message details popup screen
"""
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import (
    Button,
    Label,
    Pretty,
    Static,
    RichLog
)
from textual.binding import Binding
from rich.syntax import Syntax
from ..core.messages import Message, MessageType
import json

class MessageDetailsScreen(ModalScreen[bool]):
    """Detailed message view screen"""
    
    BINDINGS = [
        Binding("escape", "dismiss(False)", "Close"),
        Binding("c", "copy", "Copy"),
        Binding("e", "export", "Export"),
    ]
    
    def __init__(self, message: Message):
        """Initialize with a message
        
        Args:
            message: The message to display
        """
        super().__init__()
        self.message = message
        
    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Container(
            Container(
                Label("Message Details", id="title", classes="modal-title"),
                Button("×", id="close", classes="close-button"),
                classes="modal-header"
            ),
            Container(
                Vertical(
                    # Message basics
                    Container(
                        Label("Time:", classes="detail-label"),
                        Label(self.message.timestamp.strftime("%Y-%m-%d %H:%M:%S"), classes="detail-value"),
                        classes="detail-row"
                    ),
                    Container(
                        Label("Type:", classes="detail-label"),
                        Label(self.message.type.value.upper(), classes="detail-value"),
                        classes="detail-row"
                    ),
                    Container(
                        Label("Source:", classes="detail-label"),
                        Label(self.message.source, classes="detail-value"),
                        classes="detail-row"
                    ),
                    Container(
                        Label("Message:", classes="detail-label"),
                        Label(self.message.text, classes="detail-value"),
                        classes="detail-row"
                    ),
                    # Progress if available
                    Container(
                        Label("Progress:", classes="detail-label"),
                        Label(
                            f"{self.message.progress:.1f}%" if self.message.progress is not None else "N/A",
                            classes="detail-value"
                        ),
                        classes="detail-row",
                        id="progress-container"
                    ),
                    # Details section
                    Container(
                        Label("Details:", classes="detail-label"),
                        ScrollableContainer(
                            Pretty(self.message.details) if self.message.details else Label("No additional details"),
                            classes="detail-value"
                        ),
                        classes="detail-row"
                    ),
                    id="details-container"
                ),
                Horizontal(
                    Button("Copy to Clipboard", variant="primary", id="copy"),
                    Button("Export to File", variant="default", id="export"),
                    Button("Close", variant="default", id="dismiss"),
                    classes="button-container"
                ),
                classes="modal-content"
            ),
            classes="modal-container"
        )
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "close" or event.button.id == "dismiss":
            self.dismiss(False)
        elif event.button.id == "copy":
            self.action_copy()
        elif event.button.id == "export":
            self.action_export()
            
    def action_copy(self) -> None:
        """Copy message details to clipboard"""
        details = {
            "time": self.message.timestamp.isoformat(),
            "type": self.message.type.value,
            "source": self.message.source,
            "message": self.message.text,
            "progress": self.message.progress,
            "details": self.message.details
        }
        
        try:
            import pyperclip
            pyperclip.copy(json.dumps(details, indent=2))
            self.notify("Message details copied to clipboard", severity="success")
        except ImportError:
            self.notify("pyperclip not installed - cannot copy to clipboard", severity="error")
            
    def action_export(self) -> None:
        """Export message details to file"""
        from pathlib import Path
        import json
        
        try:
            export_dir = Path.home() / ".local" / "share" / "repo_tool" / "exports"
            export_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"message_{self.message.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            export_path = export_dir / filename
            
            details = {
                "time": self.message.timestamp.isoformat(),
                "type": self.message.type.value,
                "source": self.message.source,
                "message": self.message.text,
                "progress": self.message.progress,
                "details": self.message.details
            }
            
            with open(export_path, 'w') as f:
                json.dump(details, f, indent=2)
                
            self.notify(f"Message exported to {export_path}", severity="success")
        except Exception as e:
            self.notify(f"Failed to export message: {str(e)}", severity="error")

