# RepoTool Developer Guide

## Table of Contents
1. [Development Environment](#development-environment)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [TUI Components](#tui-components)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Contributing](#contributing)

## Development Environment

### Requirements
- Python 3.8+
- Node.js 14+ (for TypeScript components)
- Make
- Git
- GitHub CLI (optional)

### Setup
1. Clone repository:
```bash
git clone https://github.com/cbwinslow/repo-tool.git
cd repo-tool
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

3. Install dependencies:
```bash
make install
```

4. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Development Tools
- VS Code configuration provided
- Pre-commit hooks for linting
- Automated testing with pytest
- Documentation with Sphinx

## Project Structure

```
repo_tool/
├── docs/
│   ├── source/         # Sphinx documentation
│   ├── USER_GUIDE.md
│   └── DEVELOPER_GUIDE.md
├── src/
│   └── repo_tool/
│       ├── core/       # Core functionality
│       │   ├── auth.py
│       │   ├── config.py
│       │   ├── logger.py
│       │   ├── messages.py
│       │   └── repo_ops.py
│       ├── tui/        # TUI components
│       │   ├── app.py
│       │   ├── message_screen.py
│       │   ├── repo_screen.py
│       │   └── settings_screen.py
│       └── __main__.py
├── tests/
│   ├── conftest.py
│   ├── test_core.py
│   └── test_tui.py
├── Makefile
├── setup.py
├── README.md
└── LICENSE
```

## Core Components

### Authentication (`auth.py`)
- Secure token storage using keyring
- Service-specific token validation
- SSH key management

```python
from repo_tool.core.auth import TokenManager

# Store token
token_manager = TokenManager()
token_manager.store_token("github", "ghp_...")

# Validate token
is_valid = token_manager.validate_token("github", "ghp_...")
```

### Configuration (`config.py`)
- YAML-based configuration
- Default values
- Path management
- User settings

```python
from repo_tool.core.config import Config

# Load config
config = Config()
download_path = config.get_download_path()

# Update setting
config.set("display.theme", "dark")
```

### Repository Operations (`repo_ops.py`)
- Repository creation
- Downloading
- Issue management
- Service integration

```python
from repo_tool.core.repo_ops import RepositoryOperations

# Create repository
repo_ops = RepositoryOperations()
new_repo = repo_ops.create_repository(
    RepoCreateOptions(
        name="new-repo",
        description="Test repository"
    )
)
```

### Message Center (`messages.py`)
- Message tracking
- Progress updates
- Statistical analysis
- Export functionality

```python
from repo_tool.core.messages import MessageCenter, MessageType

# Add message
message_center = MessageCenter()
message_center.add_message(
    "Repository created",
    type=MessageType.SUCCESS,
    source="repo_ops"
)
```

## TUI Components

### Main Application (`app.py`)
- Entry point
- Screen management
- Global state
- Event handling

```python
from repo_tool.tui.app import RepoToolApp

def main():
    app = RepoToolApp()
    app.run()
```

### Custom Widgets
1. Create widget class:
```python
from textual.widgets import Static

class ProgressWidget(Static):
    def __init__(self):
        super().__init__()
        self.progress = 0

    def render(self):
        return f"Progress: {self.progress}%"
```

2. Use in screens:
```python
from textual.app import ComposeResult

def compose(self) -> ComposeResult:
    yield ProgressWidget()
```

### Screen Lifecycle
1. Initialize:
```python
def __init__(self):
    super().__init__()
    self.load_data()
```

2. Mount:
```python
def on_mount(self):
    self.query_one("#progress").update()
```

3. Unmount:
```python
def on_unmount(self):
    self.save_state()
```

## Testing

### Unit Tests
```python
def test_config_creation(config):
    assert config.get("theme") == "dark"
    assert isinstance(config.get_download_path(), Path)
```

### Integration Tests
```python
def test_repository_download(temp_dir):
    repo_ops = RepositoryOperations()
    repo = repo_ops.create_repository(...)
    repo_ops.download_repository(repo, temp_dir)
    assert (temp_dir / repo.name).exists()
```

### Running Tests
```bash
# All tests
make test

# Specific test
pytest tests/test_core.py -k test_config

# With coverage
pytest --cov=repo_tool
```

## Documentation

### Code Documentation
- Use Google-style docstrings
- Include type hints
- Document exceptions

```python
def create_repository(
    self,
    options: RepoCreateOptions,
    service: str = "github"
) -> RepoInfo:
    """Create a new repository.

    Args:
        options: Repository creation options
        service: Service to create repository on

    Returns:
        RepoInfo: Information about created repository

    Raises:
        ValueError: If service is not supported
        AuthenticationError: If token is invalid
    """
```

### Building Documentation
```bash
# Generate HTML
make docs

# Generate PDF
make docs-pdf
```

## Contributing

### Workflow
1. Fork repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Update documentation
6. Submit pull request

### Guidelines
- Follow PEP 8
- Add type hints
- Write tests
- Update documentation
- Keep commits atomic

### Pre-commit Checks
```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Release Process
1. Update version in setup.py
2. Update CHANGELOG.md
3. Create release branch
4. Run tests
5. Build documentation
6. Create GitHub release
7. Upload to PyPI

### Versioning
- Follow semantic versioning
- Format: MAJOR.MINOR.PATCH
- Update CHANGELOG.md

