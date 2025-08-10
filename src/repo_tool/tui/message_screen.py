"""
Message center screen for the TUI
"""
from textual.app import ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Label,
    Tabs,
    Tab,
    Footer
)
from textual.binding import Binding
from datetime import datetime, timedelta
from ..core.messages import MessageCenter, MessageType, Message

class MessageCenterScreen(Screen):
    """Message center screen"""
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("c", "clear", "Clear Messages"),
        Binding("r", "refresh", "Refresh"),
        Binding("f", "filter", "Filter"),
    ]
    
    def __init__(self):
        super().__init__()
        self.message_center = MessageCenter()
        
    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Container(
            Label("Message Center", id="title"),
            Tabs(
                Tab("All", id="all"),
                Tab("Info", id="info"),
                Tab("Success", id="success"),
                Tab("Warning", id="warning"),
                Tab("Error", id="error"),
                Tab("Progress", id="progress"),
                id="message-tabs"
            ),
            ScrollableContainer(
                DataTable(
                    show_header=True,
                    zebra_stripes=True,
                    id="message-table"
                )
            ),
            Label("", id="status"),
            Footer()
        )
        
    def on_mount(self) -> None:
        """Handle screen mount"""
        table = self.query_one("#message-table", DataTable)
        table.add_columns(
            "Time",
            "Type",
            "Source",
            "Message",
            "Progress"
        )
        self.load_messages()
        
    def load_messages(self, message_type: MessageType = None) -> None:
        """Load messages into the table"""
        table = self.query_one("#message-table", DataTable)
        table.clear()
        
        # Get messages from the last 7 days by default
        since = datetime.now() - timedelta(days=7)
        messages = self.message_center.get_messages(
            type=message_type,
            since=since
        )
        
        for msg in messages:
            progress = f"{msg.progress:.1f}%" if msg.progress is not None else ""
            table.add_row(
                msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                msg.type.value.upper(),
                msg.source,
                msg.text,
                progress,
                key=str(msg.timestamp.timestamp())
            )
            
        status = self.query_one("#status", Label)
        status.update(f"Showing {len(messages)} messages")
        
    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle tab changes"""
        tab_id = event.tab.id
        if tab_id == "all":
            self.load_messages()
        else:
            self.load_messages(MessageType(tab_id))
            
    def action_clear(self) -> None:
        """Clear messages"""
        tab = self.query_one("Tabs").active_tab
        message_type = None if tab.id == "all" else MessageType(tab.id)
        
        # Clear messages older than 7 days
        older_than = datetime.now() - timedelta(days=7)
        cleared = self.message_center.clear_messages(
            older_than=older_than,
            type=message_type
        )
        
        self.notify(f"Cleared {cleared} messages", severity="info")
        self.load_messages(message_type)
        
    def action_refresh(self) -> None:
        """Refresh message list"""
        tab = self.query_one("Tabs").active_tab
        message_type = None if tab.id == "all" else MessageType(tab.id)
        self.load_messages(message_type)
        
    def action_back(self) -> None:
        """Return to previous screen"""
        self.dismiss()
        
    def action_filter(self) -> None:
        """Toggle filter input"""
        table = self.query_one("#message-table", DataTable)
        table.focus()
        
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection"""
        # TODO: Show message details in a popup
        pass

