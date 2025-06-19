"""
Error documentation and troubleshooting screen
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import (
    Button,
    Label,
    Tree,
    Static,
    Input,
    RichLog,
    Footer,
    DataTable
)
from textual.binding import Binding
from textual.message import Message
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from pathlib import Path
import yaml

class ErrorInfo:
    """Error information structure"""
    
    def __init__(self, code: str, title: str, description: str, causes: list, solutions: list):
        self.code = code
        self.title = title
        self.description = description
        self.causes = causes
        self.solutions = solutions
        
    @classmethod
    def from_dict(cls, data: dict) -> 'ErrorInfo':
        """Create from dictionary"""
        return cls(
            code=data["code"],
            title=data["title"],
            description=data["description"],
            causes=data.get("causes", []),
            solutions=data.get("solutions", [])
        )

class ErrorScreen(Screen):
    """Error documentation and troubleshooting screen"""
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("s", "search", "Search"),
        Binding("/", "search", "Search"),
        Binding("h", "help", "Help"),
    ]
    
    def __init__(self):
        super().__init__()
        self.errors = self.load_error_docs()
        self.current_error = None
        
    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Container(
            Label("Error Documentation", id="title"),
            Horizontal(
                # Error list
                Container(
                    Label("Error Categories", classes="section-title"),
                    Input(placeholder="Search errors...", id="search-input"),
                    Tree("Errors", id="error-tree"),
                    classes="tree-container"
                ),
                # Error details
                Container(
                    Label("Error Details", classes="section-title"),
                    ScrollableContainer(
                        RichLog(id="error-details", wrap=True),
                        classes="details-container"
                    ),
                    classes="content-container"
                ),
                id="main-container"
            ),
            Horizontal(
                Button("Back", variant="primary", id="back"),
                Button("Help", variant="default", id="help"),
                classes="button-container"
            ),
            Footer()
        )
        
    def load_error_docs(self) -> dict:
        """Load error documentation"""
        try:
            docs_path = Path(__file__).parent.parent / "data" / "errors.yaml"
            with open(docs_path) as f:
                data = yaml.safe_load(f)
                
            errors = {}
            for category, items in data.items():
                category_errors = {}
                for item in items:
                    error = ErrorInfo.from_dict(item)
                    category_errors[error.code] = error
                errors[category] = category_errors
                
            return errors
        except Exception as e:
            return {
                "Authentication": {
                    "AUTH001": ErrorInfo(
                        code="AUTH001",
                        title="Token validation failed",
                        description="Failed to validate service authentication token",
                        causes=[
                            "Invalid token format",
                            "Expired token",
                            "Insufficient permissions"
                        ],
                        solutions=[
                            "Check token in service settings",
                            "Generate new token with required scopes",
                            "Verify token has not expired"
                        ]
                    )
                },
                "Network": {
                    "NET001": ErrorInfo(
                        code="NET001",
                        title="Connection failed",
                        description="Failed to connect to service API",
                        causes=[
                            "Network connectivity issues",
                            "Service API unreachable",
                            "Invalid API endpoint"
                        ],
                        solutions=[
                            "Check network connection",
                            "Verify service status",
                            "Check API endpoint configuration"
                        ]
                    )
                },
                "Repository": {
                    "REPO001": ErrorInfo(
                        code="REPO001",
                        title="Repository not found",
                        description="Unable to find specified repository",
                        causes=[
                            "Repository does not exist",
                            "Insufficient permissions",
                            "Invalid repository name"
                        ],
                        solutions=[
                            "Verify repository exists",
                            "Check access permissions",
                            "Verify repository name format"
                        ]
                    )
                }
            }
            
    def on_mount(self) -> None:
        """Handle screen mount"""
        self.build_error_tree()
        
    def build_error_tree(self) -> None:
        """Build error tree"""
        tree = self.query_one("#error-tree", Tree)
        tree.clear()
        
        for category, errors in self.errors.items():
            category_node = tree.root.add(category)
            for error_code, error in errors.items():
                category_node.add_leaf(f"{error_code}: {error.title}")
                
    def show_error_details(self, error: ErrorInfo) -> None:
        """Show error details"""
        details = self.query_one("#error-details", RichLog)
        details.clear()
        
        details.write(f"# {error.code}: {error.title}\n", style="bold")
        details.write(f"\n{error.description}\n\n")
        
        details.write("## Possible Causes\n", style="bold yellow")
        for cause in error.causes:
            details.write(f"- {cause}")
        details.write("\n")
        
        details.write("## Solutions\n", style="bold green")
        for i, solution in enumerate(error.solutions, 1):
            details.write(f"{i}. {solution}")
        details.write("\n")
        
        # Add example if available
        example = self.get_error_example(error.code)
        if example:
            details.write("## Example\n", style="bold blue")
            details.write("```python\n")
            details.write(example)
            details.write("\n```")
            
    def get_error_example(self, error_code: str) -> str:
        """Get example code for error"""
        examples = {
            "AUTH001": """
try:
    token_manager.validate_token("github", token)
except AuthenticationError as e:
    logger.error(f"Token validation failed: {e}")
    # Handle token validation failure
""",
            "NET001": """
try:
    response = requests.get(api_url, timeout=30)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logger.error(f"API request failed: {e}")
    # Handle connection failure
""",
            "REPO001": """
try:
    repo = github.get_repo(f"{owner}/{repo_name}")
except github.GithubException as e:
    if e.status == 404:
        logger.error(f"Repository not found: {owner}/{repo_name}")
        # Handle repository not found
    else:
        raise
"""
        }
        return examples.get(error_code)
        
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection"""
        if ":" in event.node.label:
            error_code = event.node.label.split(":")[0].strip()
            category = event.node.parent.label
            if category in self.errors and error_code in self.errors[category]:
                self.current_error = self.errors[category][error_code]
                self.show_error_details(self.current_error)
                
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes"""
        search = event.value.lower()
        tree = self.query_one("#error-tree", Tree)
        tree.clear()
        
        for category, errors in self.errors.items():
            category_node = None
            for error_code, error in errors.items():
                if (search in error_code.lower() or
                    search in error.title.lower() or
                    search in error.description.lower()):
                    if category_node is None:
                        category_node = tree.root.add(category)
                    category_node.add_leaf(f"{error_code}: {error.title}")
                    
    def action_help(self) -> None:
        """Show help information"""
        details = self.query_one("#error-details", RichLog)
        details.clear()
        
        details.write("# Using Error Documentation\n\n", style="bold")
        details.write("## Navigation\n", style="bold yellow")
        details.write("- Use arrow keys to navigate error tree\n")
        details.write("- Press Enter to select an error\n")
        details.write("- Use / or s to search errors\n")
        details.write("- Press Escape to go back\n\n")
        
        details.write("## Search Tips\n", style="bold green")
        details.write("- Search by error code (e.g., AUTH001)\n")
        details.write("- Search by keywords in title or description\n")
        details.write("- Search is case-insensitive\n\n")
        
        details.write("## Error Categories\n", style="bold blue")
        details.write("- Authentication: Token and credential issues\n")
        details.write("- Network: Connection and API problems\n")
        details.write("- Repository: Repository access and management\n")
        
    def action_back(self) -> None:
        """Return to previous screen"""
        self.dismiss()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "help":
            self.action_help()
        elif event.button.id == "back":
            self.dismiss()

