"""
Diagnostic screen for system information and troubleshooting
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer, Grid
from textual.widgets import (
    Button,
    Label,
    Static,
    ProgressBar,
    TreeControl,
    Tree,
    RichLog,
    Footer,
    DataTable
)
from textual.binding import Binding
from textual.message import Message
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
import psutil
import platform
import os
import sys
import json
from pathlib import Path
from datetime import datetime

from ..core.config import Config
from ..core.messages import MessageCenter
from ..core.logger import get_logger

class SystemMonitor:
    """System resource monitoring"""
    
    @staticmethod
    def get_cpu_info():
        """Get CPU information"""
        return {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(),
            "freq": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "load": [x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]
        }
        
    @staticmethod
    def get_memory_info():
        """Get memory information"""
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "percent": mem.percent,
            "used": mem.used,
            "free": mem.free
        }
        
    @staticmethod
    def get_disk_info():
        """Get disk information"""
        disk = psutil.disk_usage("/")
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
        
    @staticmethod
    def get_network_info():
        """Get network information"""
        net = psutil.net_io_counters()
        return {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
            "errin": net.errin,
            "errout": net.errout
        }

class DiagnosticScreen(Screen):
    """System diagnostic and troubleshooting screen"""
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("r", "refresh", "Refresh"),
        Binding("s", "save", "Save Report"),
        Binding("t", "test", "Run Tests"),
        Binding("c", "cleanup", "Cleanup"),
    ]
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.message_center = MessageCenter()
        self.logger = get_logger(__name__)
        self.monitor = SystemMonitor()
        
    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Container(
            Label("System Diagnostics", id="title"),
            Grid(
                # System Information
                Container(
                    Label("System Information", classes="section-title"),
                    RichLog(id="system-info", wrap=True),
                    classes="info-panel"
                ),
                # Resource Usage
                Container(
                    Label("Resource Usage", classes="section-title"),
                    Vertical(
                        Label("CPU Usage:"),
                        ProgressBar(id="cpu-progress"),
                        Label("Memory Usage:"),
                        ProgressBar(id="memory-progress"),
                        Label("Disk Usage:"),
                        ProgressBar(id="disk-progress"),
                    ),
                    classes="resource-panel"
                ),
                # Component Status
                Container(
                    Label("Component Status", classes="section-title"),
                    DataTable(id="status-table"),
                    classes="status-panel"
                ),
                # Log View
                Container(
                    Label("Recent Logs", classes="section-title"),
                    RichLog(id="log-view", wrap=True),
                    classes="log-panel"
                ),
                id="diagnostic-grid"
            ),
            Horizontal(
                Button("Refresh", variant="primary", id="refresh"),
                Button("Run Tests", variant="default", id="test"),
                Button("Save Report", variant="default", id="save"),
                Button("Cleanup", variant="warning", id="cleanup"),
                Button("Back", variant="default", id="back"),
                classes="button-container"
            ),
            Footer()
        )
        
    def on_mount(self) -> None:
        """Handle screen mount"""
        self.load_system_info()
        self.load_resource_usage()
        self.load_component_status()
        self.load_recent_logs()
        
    def load_system_info(self) -> None:
        """Load system information"""
        info = RichLog(id="system-info")
        
        # Python information
        info.write("Python Environment:", style="bold")
        info.write(f"Version: {sys.version.split()[0]}")
        info.write(f"Implementation: {platform.python_implementation()}")
        info.write(f"Path: {sys.executable}")
        info.write("")
        
        # Platform information
        info.write("Platform:", style="bold")
        info.write(f"OS: {platform.system()} {platform.release()}")
        info.write(f"Machine: {platform.machine()}")
        info.write(f"Processor: {platform.processor()}")
        info.write("")
        
        # Environment variables
        info.write("Environment:", style="bold")
        info.write(f"LANG: {os.environ.get('LANG', 'Not set')}")
        info.write(f"TERM: {os.environ.get('TERM', 'Not set')}")
        info.write(f"SHELL: {os.environ.get('SHELL', 'Not set')}")
        info.write("")
        
        # Application paths
        info.write("Application Paths:", style="bold")
        info.write(f"Config: {self.config.config_dir}")
        info.write(f"Cache: {Path.home() / '.cache' / 'repo_tool'}")
        info.write(f"Logs: {Path.home() / '.local' / 'share' / 'repo_tool' / 'logs'}")
        
    def load_resource_usage(self) -> None:
        """Load resource usage information"""
        # CPU usage
        cpu_info = self.monitor.get_cpu_info()
        self.query_one("#cpu-progress").update(
            progress=cpu_info["percent"],
            total=100
        )
        
        # Memory usage
        mem_info = self.monitor.get_memory_info()
        self.query_one("#memory-progress").update(
            progress=mem_info["percent"],
            total=100
        )
        
        # Disk usage
        disk_info = self.monitor.get_disk_info()
        self.query_one("#disk-progress").update(
            progress=disk_info["percent"],
            total=100
        )
        
    def load_component_status(self) -> None:
        """Load component status information"""
        table = self.query_one("#status-table", DataTable)
        table.clear()
        table.add_columns("Component", "Status", "Details")
        
        # Check configuration
        config_status = "OK" if self.config.config_file.exists() else "Missing"
        table.add_row(
            "Configuration",
            config_status,
            self.config.config_file
        )
        
        # Check database
        db_path = Path.home() / ".local" / "share" / "repo_tool" / "messages.db"
        db_status = "OK" if db_path.exists() else "Missing"
        table.add_row(
            "Message Database",
            db_status,
            str(db_path)
        )
        
        # Check logs
        log_path = Path.home() / ".local" / "share" / "repo_tool" / "logs"
        log_status = "OK" if log_path.exists() else "Missing"
        table.add_row(
            "Log Directory",
            log_status,
            str(log_path)
        )
        
        # Check tokens
        for service in ["github", "gitlab", "bitbucket"]:
            token = self.config.get(f"services.{service}.token")
            status = "Configured" if token else "Not configured"
            table.add_row(
                f"{service.title()} Token",
                status,
                "Token present" if token else "No token"
            )
            
    def load_recent_logs(self) -> None:
        """Load recent log entries"""
        log_view = self.query_one("#log-view", RichLog)
        log_view.clear()
        
        try:
            log_path = Path.home() / ".local" / "share" / "repo_tool" / "logs" / "repo_tool.log"
            if log_path.exists():
                with open(log_path) as f:
                    last_lines = list(f)[-50:]  # Last 50 lines
                    for line in last_lines:
                        if "ERROR" in line:
                            log_view.write(line.strip(), style="red")
                        elif "WARNING" in line:
                            log_view.write(line.strip(), style="yellow")
                        else:
                            log_view.write(line.strip())
            else:
                log_view.write("No log file found", style="italic")
        except Exception as e:
            log_view.write(f"Error reading logs: {e}", style="red")
            
    def action_refresh(self) -> None:
        """Refresh all information"""
        self.load_system_info()
        self.load_resource_usage()
        self.load_component_status()
        self.load_recent_logs()
        
    def action_save(self) -> None:
        """Save diagnostic report"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "python": sys.version,
                    "platform": platform.platform(),
                    "machine": platform.machine(),
                    "processor": platform.processor()
                },
                "resources": {
                    "cpu": self.monitor.get_cpu_info(),
                    "memory": self.monitor.get_memory_info(),
                    "disk": self.monitor.get_disk_info(),
                    "network": self.monitor.get_network_info()
                },
                "config": self.config.config,
                "environment": dict(os.environ)
            }
            
            report_dir = Path.home() / ".local" / "share" / "repo_tool" / "reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            
            report_path = report_dir / f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
                
            self.notify(f"Report saved to {report_path}", severity="success")
        except Exception as e:
            self.notify(f"Failed to save report: {e}", severity="error")
            
    def action_test(self) -> None:
        """Run diagnostic tests"""
        self.notify("Running diagnostic tests...", severity="info")
        # This would be implemented to run various tests
        
    def action_cleanup(self) -> None:
        """Clean up temporary files and optimize storage"""
        try:
            # Clear old logs
            log_dir = Path.home() / ".local" / "share" / "repo_tool" / "logs"
            for log in log_dir.glob("*.log.*"):
                if log.stat().st_mtime < (datetime.now().timestamp() - 30 * 86400):
                    log.unlink()
                    
            # Clear cache
            cache_dir = Path.home() / ".cache" / "repo_tool"
            if cache_dir.exists():
                for item in cache_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                        
            # Optimize database
            self.message_center._optimize_db()
            
            self.notify("Cleanup completed successfully", severity="success")
        except Exception as e:
            self.notify(f"Cleanup failed: {e}", severity="error")
            
    def action_back(self) -> None:
        """Return to previous screen"""
        self.dismiss()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "refresh":
            self.action_refresh()
        elif event.button.id == "save":
            self.action_save()
        elif event.button.id == "test":
            self.action_test()
        elif event.button.id == "cleanup":
            self.action_cleanup()
        elif event.button.id == "back":
            self.dismiss()

