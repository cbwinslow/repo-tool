# RepoTool

A powerful Terminal User Interface (TUI) application for managing and downloading repositories from GitHub, GitLab, and Bitbucket.

## Features

### Repository Management
- Browse, search, and manage repositories across multiple services
- Create new repositories with templates and license selection
- Fork repositories to your account or organization
- Create and manage issues
- Delete repositories with confirmation
- Download repositories with progress tracking
- Support for multiple repository selection
- Batch operations via text file input

### Authentication & Security
- Secure PAT (Personal Access Token) storage using system keyring
- Support for GitHub CLI integration
- SSH key support for all services
- Token validation and secure storage
- Automatic token refresh

### User Interface
- Modern TUI with mouse and keyboard support
- Progress bars for all operations
- Message center for status updates and errors
- Multiple repository selection
- Dark and light themes
- Configurable UI elements

### Configuration
- User-configurable settings via TUI
- Automatic git configuration detection
- Default paths configuration
- Service-specific settings
- Configuration file support (~/.config/repo_tool/config.yaml)

### Logging & Error Handling
- Comprehensive error handling and validation
- Detailed logging with rotation
- Message center for user feedback
- Error reporting and debugging tools

### Updates & Maintenance
- Automatic update checking
- Built-in update mechanism
- Cross-platform support
- Multiple distribution formats (DEB, Snap, Flatpak)

## Installation

### From Source

1. Clone the repository:
```bash
git clone https://github.com/yourusername/repo-tool.git
cd repo-tool
```

2. Install with make:
```bash
make install
```

### Using Package Managers

#### DEB Package (Ubuntu/Debian)
```bash
sudo dpkg -i repo-tool_1.0.0_all.deb
```

#### Snap Package
```bash
sudo snap install repo-tool
```

#### Flatpak
```bash
flatpak install repo-tool
```

## Usage

1. Launch the application:
```bash
repo-tool
```

2. First-time setup:
   - Enter your authentication tokens for the services you want to use
   - Configure default download location
   - Select your preferred theme

3. Using the interface:
   - Use arrow keys or mouse to navigate
   - Press 'h' for help
   - Press 'q' to quit
   - Press 'r' to refresh repository list
   - Press 's' for settings

## Configuration

Configuration is stored in `~/.config/repo_tool/config.yaml`. You can modify:

- Default download location
- Theme preferences
- Update check frequency
- Logging level
- Enabled services

## Development

### Requirements

- Python 3.8+
- Node.js (for TypeScript components)
- Make

### Setup Development Environment

```bash
make install
```

### Running Tests

```bash
make test
```

### Building Documentation

```bash
make docs
```

### Code Style

The project uses:
- flake8 and mypy for Python
- eslint for TypeScript

Run linting:
```bash
make lint
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Textual](https://github.com/Textualize/textual)
- Inspired by various terminal-based tools like `gh` and `lab`

