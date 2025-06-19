"""
Message statistics screen
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.widgets import (
    Label,
    BarChart,
    LineChart,
    DataTable,
    Button
)
from textual.binding import Binding
from datetime import datetime, timedelta
from collections import defaultdict
from ..core.messages import MessageCenter, MessageType

class MessageStatsScreen(Screen):
    """Message statistics and analytics screen"""
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("t", "toggle_view", "Toggle View"),
    ]
    
    def __init__(self):
        super().__init__()
        self.message_center = MessageCenter()
        self.view_mode = "daily"  # or "hourly"
        
    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Container(
            Label("Message Statistics", id="title"),
            Grid(
                # Message type distribution
                Container(
                    Label("Message Distribution", classes="chart-title"),
                    BarChart(id="type-chart"),
                    classes="chart-container"
                ),
                # Message volume over time
                Container(
                    Label("Message Volume", classes="chart-title"),
                    LineChart(id="volume-chart"),
                    classes="chart-container"
                ),
                # Message source distribution
                Container(
                    Label("Top Sources", classes="chart-title"),
                    BarChart(id="source-chart"),
                    classes="chart-container"
                ),
                # Summary statistics
                Container(
                    Label("Summary", classes="chart-title"),
                    DataTable(id="stats-table"),
                    classes="chart-container"
                ),
                id="stats-grid"
            ),
            Horizontal(
                Button("Daily View", id="daily-view", variant="primary"),
                Button("Hourly View", id="hourly-view", variant="default"),
                Button("Export Stats", id="export-stats", variant="default"),
                classes="button-container"
            )
        )
        
    def on_mount(self) -> None:
        """Handle screen mount"""
        self.load_statistics()
        
    def get_message_stats(self):
        """Calculate message statistics"""
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        messages = self.message_center.get_messages(since=week_ago)
        
        # Type distribution
        type_counts = defaultdict(int)
        # Source distribution
        source_counts = defaultdict(int)
        # Volume over time
        volume_by_time = defaultdict(int)
        
        for msg in messages:
            type_counts[msg.type.value] += 1
            source_counts[msg.source] += 1
            
            if self.view_mode == "daily":
                time_key = msg.timestamp.strftime("%Y-%m-%d")
            else:
                time_key = msg.timestamp.strftime("%Y-%m-%d %H:00")
            volume_by_time[time_key] += 1
            
        return {
            "type_counts": dict(type_counts),
            "source_counts": dict(sorted(
                source_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),  # Top 10 sources
            "volume_by_time": dict(sorted(volume_by_time.items())),
            "total_messages": len(messages),
            "unique_sources": len(source_counts),
            "error_rate": (type_counts.get("error", 0) / len(messages)) if messages else 0
        }
        
    def load_statistics(self) -> None:
        """Load and display statistics"""
        stats = self.get_message_stats()
        
        # Update type distribution chart
        type_chart = self.query_one("#type-chart", BarChart)
        type_chart.clear()
        for msg_type, count in stats["type_counts"].items():
            type_chart.add_value(label=msg_type.upper(), value=count)
            
        # Update volume chart
        volume_chart = self.query_one("#volume-chart", LineChart)
        volume_chart.clear()
        volume_chart.add_series(
            "Messages",
            list(stats["volume_by_time"].values()),
            list(stats["volume_by_time"].keys())
        )
        
        # Update source chart
        source_chart = self.query_one("#source-chart", BarChart)
        source_chart.clear()
        for source, count in stats["source_counts"].items():
            source_chart.add_value(label=source, value=count)
            
        # Update summary table
        table = self.query_one("#stats-table", DataTable)
        table.clear()
        table.add_columns("Metric", "Value")
        table.add_rows([
            ("Total Messages", str(stats["total_messages"])),
            ("Unique Sources", str(stats["unique_sources"])),
            ("Error Rate", f"{stats['error_rate']:.2%}"),
            ("Most Common Type", max(
                stats["type_counts"].items(),
                key=lambda x: x[1]
            )[0].upper() if stats["type_counts"] else "N/A"),
            ("Most Active Source", max(
                stats["source_counts"].items(),
                key=lambda x: x[1]
            )[0] if stats["source_counts"] else "N/A")
        ])
        
    def action_refresh(self) -> None:
        """Refresh statistics"""
        self.load_statistics()
        
    def action_back(self) -> None:
        """Return to previous screen"""
        self.dismiss()
        
    def action_toggle_view(self) -> None:
        """Toggle between daily and hourly views"""
        self.view_mode = "hourly" if self.view_mode == "daily" else "daily"
        self.load_statistics()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "daily-view":
            self.view_mode = "daily"
            event.button.variant = "primary"
            self.query_one("#hourly-view", Button).variant = "default"
            self.load_statistics()
        elif event.button.id == "hourly-view":
            self.view_mode = "hourly"
            event.button.variant = "primary"
            self.query_one("#daily-view", Button).variant = "default"
            self.load_statistics()
        elif event.button.id == "export-stats":
            self.export_statistics()
            
    def export_statistics(self) -> None:
        """Export statistics to file"""
        from pathlib import Path
        import json
        
        try:
            export_dir = Path.home() / ".local" / "share" / "repo_tool" / "exports"
            export_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"message_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_path = export_dir / filename
            
            stats = self.get_message_stats()
            # Convert datetime keys to strings
            stats["volume_by_time"] = {
                str(k): v for k, v in stats["volume_by_time"].items()
            }
            
            with open(export_path, 'w') as f:
                json.dump(stats, f, indent=2)
                
            self.notify(f"Statistics exported to {export_path}", severity="success")
        except Exception as e:
            self.notify(f"Failed to export statistics: {str(e)}", severity="error")

