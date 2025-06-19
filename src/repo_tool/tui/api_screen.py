"""
API documentation and examples screen
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

class ApiEndpoint:
    """API endpoint documentation"""
    
    def __init__(
        self,
        name: str,
        method: str,
        path: str,
        description: str,
        parameters: list,
        responses: dict,
        example_request: str = None,
        example_response: str = None
    ):
        self.name = name
        self.method = method
        self.path = path
        self.description = description
        self.parameters = parameters
        self.responses = responses
        self.example_request = example_request
        self.example_response = example_response

class ApiScreen(Screen):
    """API documentation screen"""
    
    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("s", "search", "Search"),
        Binding("/", "search", "Search"),
        Binding("h", "help", "Help"),
    ]
    
    def __init__(self):
        super().__init__()
        self.apis = self.load_api_docs()
        self.current_endpoint = None
        
    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Container(
            Label("API Documentation", id="title"),
            Horizontal(
                # API list
                Container(
                    Label("API Endpoints", classes="section-title"),
                    Input(placeholder="Search APIs...", id="search-input"),
                    Tree("APIs", id="api-tree"),
                    classes="tree-container"
                ),
                # API details
                Container(
                    Label("Endpoint Details", classes="section-title"),
                    ScrollableContainer(
                        RichLog(id="api-details", wrap=True),
                        classes="details-container"
                    ),
                    classes="content-container"
                ),
                id="main-container"
            ),
            Horizontal(
                Button("Back", variant="primary", id="back"),
                Button("Help", variant="default", id="help"),
                Button("Copy Example", variant="default", id="copy"),
                classes="button-container"
            ),
            Footer()
        )
        
    def load_api_docs(self) -> dict:
        """Load API documentation"""
        return {
            "GitHub": {
                "List Repositories": ApiEndpoint(
                    name="List Repositories",
                    method="GET",
                    path="/user/repos",
                    description="List repositories for the authenticated user",
                    parameters=[
                        {
                            "name": "visibility",
                            "type": "string",
                            "description": "Filter by repository visibility",
                            "enum": ["all", "public", "private"]
                        },
                        {
                            "name": "sort",
                            "type": "string",
                            "description": "Sort by field",
                            "enum": ["created", "updated", "pushed", "full_name"]
                        }
                    ],
                    responses={
                        "200": "List of repositories",
                        "401": "Requires authentication",
                        "403": "Forbidden"
                    },
                    example_request="""
import github

g = Github(token)
repos = g.get_user().get_repos(visibility='all')
for repo in repos:
    print(f"{repo.full_name}: {repo.description}")
""",
                    example_response="""
[
    {
        "id": 1296269,
        "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
        "name": "Hello-World",
        "full_name": "octocat/Hello-World",
        "owner": {
            "login": "octocat",
            "id": 1
        }
    }
]
"""
                ),
                "Create Repository": ApiEndpoint(
                    name="Create Repository",
                    method="POST",
                    path="/user/repos",
                    description="Create a new repository for the authenticated user",
                    parameters=[
                        {
                            "name": "name",
                            "type": "string",
                            "required": True,
                            "description": "Repository name"
                        },
                        {
                            "name": "description",
                            "type": "string",
                            "description": "Repository description"
                        },
                        {
                            "name": "private",
                            "type": "boolean",
                            "description": "Whether the repository is private"
                        }
                    ],
                    responses={
                        "201": "Repository created",
                        "400": "Bad request",
                        "401": "Requires authentication",
                        "422": "Validation failed"
                    },
                    example_request="""
from github import Github

g = Github(token)
user = g.get_user()
repo = user.create_repository(
    name="test-repo",
    description="Test repository",
    private=True
)
""",
                    example_response="""
{
    "id": 1296269,
    "node_id": "MDEwOlJlcG9zaXRvcnkxMjk2MjY5",
    "name": "test-repo",
    "full_name": "user/test-repo",
    "private": true
}
"""
                )
            },
            "GitLab": {
                "List Projects": ApiEndpoint(
                    name="List Projects",
                    method="GET",
                    path="/projects",
                    description="Get a list of visible projects for the authenticated user",
                    parameters=[
                        {
                            "name": "owned",
                            "type": "boolean",
                            "description": "Limit to projects owned by the user"
                        },
                        {
                            "name": "search",
                            "type": "string",
                            "description": "Search projects by name"
                        }
                    ],
                    responses={
                        "200": "List of projects",
                        "401": "Unauthorized",
                        "403": "Forbidden"
                    },
                    example_request="""
import gitlab

gl = gitlab.Gitlab('https://gitlab.com', private_token=token)
projects = gl.projects.list(owned=True)
for project in projects:
    print(f"{project.path_with_namespace}")
""",
                    example_response="""
[
    {
        "id": 1,
        "description": "Test Project",
        "name": "test-project",
        "name_with_namespace": "User / test-project",
        "path": "test-project",
        "path_with_namespace": "user/test-project"
    }
]
"""
                )
            }
        }
        
    def on_mount(self) -> None:
        """Handle screen mount"""
        self.build_api_tree()
        
    def build_api_tree(self) -> None:
        """Build API tree"""
        tree = self.query_one("#api-tree", Tree)
        tree.clear()
        
        for service, endpoints in self.apis.items():
            service_node = tree.root.add(service)
            for name, endpoint in endpoints.items():
                service_node.add_leaf(f"{endpoint.method} {name}")
                
    def show_endpoint_details(self, endpoint: ApiEndpoint) -> None:
        """Show endpoint details"""
        details = self.query_one("#api-details", RichLog)
        details.clear()
        
        # Basic information
        details.write(f"# {endpoint.name}\n", style="bold")
        details.write(f"\n**Method:** {endpoint.method}")
        details.write(f"\n**Path:** `{endpoint.path}`\n")
        details.write(f"\n{endpoint.description}\n")
        
        # Parameters
        if endpoint.parameters:
            details.write("\n## Parameters\n", style="bold yellow")
            for param in endpoint.parameters:
                details.write(f"### {param['name']}\n")
                details.write(f"- Type: {param['type']}")
                if "required" in param:
                    details.write(f"- Required: {param['required']}")
                details.write(f"- Description: {param['description']}")
                if "enum" in param:
                    details.write(f"- Values: {', '.join(param['enum'])}")
                details.write("\n")
                
        # Responses
        details.write("\n## Responses\n", style="bold green")
        for code, description in endpoint.responses.items():
            details.write(f"- **{code}**: {description}\n")
            
        # Example request
        if endpoint.example_request:
            details.write("\n## Example Request\n", style="bold blue")
            details.write("```python\n")
            details.write(endpoint.example_request.strip())
            details.write("\n```\n")
            
        # Example response
        if endpoint.example_response:
            details.write("\n## Example Response\n", style="bold blue")
            details.write("```json\n")
            details.write(endpoint.example_response.strip())
            details.write("\n```\n")
            
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection"""
        if event.node.parent:
            service = event.node.parent.label
            method = event.node.label.split()[0]
            name = " ".join(event.node.label.split()[1:])
            
            if service in self.apis and name in self.apis[service]:
                self.current_endpoint = self.apis[service][name]
                self.show_endpoint_details(self.current_endpoint)
                
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes"""
        search = event.value.lower()
        tree = self.query_one("#api-tree", Tree)
        tree.clear()
        
        for service, endpoints in self.apis.items():
            service_node = None
            for name, endpoint in endpoints.items():
                if (search in name.lower() or
                    search in endpoint.description.lower() or
                    search in endpoint.path.lower()):
                    if service_node is None:
                        service_node = tree.root.add(service)
                    service_node.add_leaf(f"{endpoint.method} {name}")
                    
    def action_help(self) -> None:
        """Show help information"""
        details = self.query_one("#api-details", RichLog)
        details.clear()
        
        details.write("# Using API Documentation\n\n", style="bold")
        details.write("## Navigation\n", style="bold yellow")
        details.write("- Use arrow keys to navigate API tree\n")
        details.write("- Press Enter to select an endpoint\n")
        details.write("- Use / or s to search APIs\n")
        details.write("- Press Escape to go back\n\n")
        
        details.write("## Search Tips\n", style="bold green")
        details.write("- Search by endpoint name\n")
        details.write("- Search by path\n")
        details.write("- Search by description\n")
        details.write("- Search is case-insensitive\n\n")
        
        details.write("## Using Examples\n", style="bold blue")
        details.write("- Click 'Copy Example' to copy code\n")
        details.write("- Examples use placeholder values\n")
        details.write("- Replace token with your API token\n")
        details.write("- Check response structure carefully\n")
        
    def action_copy(self) -> None:
        """Copy example code"""
        if self.current_endpoint and self.current_endpoint.example_request:
            try:
                import pyperclip
                pyperclip.copy(self.current_endpoint.example_request.strip())
                self.notify("Example code copied to clipboard", severity="success")
            except ImportError:
                self.notify("pyperclip not installed - cannot copy to clipboard", severity="error")
                
    def action_back(self) -> None:
        """Return to previous screen"""
        self.dismiss()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "help":
            self.action_help()
        elif event.button.id == "copy":
            self.action_copy()
        elif event.button.id == "back":
            self.dismiss()

