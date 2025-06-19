"""
Text viewing screen for displaying content
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, ScrollableContainer
from textual.widgets import (
    Button,
    Label,
    Static,
    Footer
)
from textual.binding import Binding

class TextScreen(Screen):
    """Screen for viewing text content"""
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("c", "copy", "Copy"),
    ]
    
    def __init__(self, title: str, content: str):
        """Initialize screen
        
        Args:
            title: Title of the content
            content: Text content to display
        """
        super().__init__()
        self.title = title
        self.content = content
        
    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Container(
            Label(self.title, id="title"),
            ScrollableContainer(
                Static(self.content, id="content"),
                id="content-scroll"
            ),
            Button("Back", variant="primary", id="back"),
            Footer()
        )
        
    def action_back(self) -> None:
        """Return to previous screen"""
        self.dismiss()
        
    def action_copy(self) -> None:
        """Copy content to clipboard"""
        try:
            import pyperclip
            pyperclip.copy(self.content)
            self.notify("Content copied to clipboard", severity="success")
        except ImportError:
            self.notify("pyperclip not installed - cannot copy to clipboard", severity="error")
            
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back":
            self.dismiss()

