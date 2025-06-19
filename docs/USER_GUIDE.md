# RepoTool User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Authentication](#authentication)
4. [Repository Management](#repository-management)
5. [Message Center](#message-center)
6. [Configuration](#configuration)
7. [Keyboard Shortcuts](#keyboard-shortcuts)
8. [Tips and Tricks](#tips-and-tricks)

## Getting Started

### Installation

1. Using pip:
```bash
pip install repo-tool
```

2. Using package managers:
```bash
# Debian/Ubuntu
sudo dpkg -i repo-tool_1.0.0_all.deb

# Snap
sudo snap install repo-tool

# Flatpak
flatpak install repo-tool
```

### First Run
1. Launch RepoTool:
```bash
repo-tool
```

2. Configure authentication:
   - Enter GitHub PAT
   - Enter GitLab PAT (optional)
   - Enter Bitbucket PAT (optional)

3. Configure default settings:
   - Download location
   - Theme preference
   - Message retention

## Basic Usage

### Main Screen
- Browse repositories
- Search functionality
- Progress tracking
- Message notifications

### Navigation
- Arrow keys for selection
- Enter to confirm
- Escape to go back
- Tab to switch focus

## Authentication

### Personal Access Tokens (PATs)
1. GitHub:
   - Visit: Settings -> Developer settings -> Personal access tokens
   - Required scopes: repo, read:org

2. GitLab:
   - Visit: User Settings -> Access Tokens
   - Required scopes: api, read_repository

3. Bitbucket:
   - Visit: Personal Settings -> App passwords
   - Required scopes: repository:read, repository:write

### SSH Keys
1. Generate key:
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
```

2. Add to services:
   - GitHub: Settings -> SSH and GPG keys
   - GitLab: User Settings -> SSH Keys
   - Bitbucket: Personal Settings -> SSH Keys

## Repository Management

### Creating Repositories
1. Press 'n' for new repository
2. Enter details:
   - Name
   - Description
   - Privacy setting
   - License
   - .gitignore template

### Downloading Repositories
1. Select repository
2. Choose download location
3. Monitor progress
4. Cancel with 'c' if needed

### Multiple Selection
1. Hold Ctrl/Cmd while clicking
2. Or use text file:
```
owner/repo1
owner/repo2
owner/repo3
```

### Batch Operations
1. Select multiple repositories
2. Choose operation:
   - Download
   - Fork
   - Star
   - Watch

## Message Center

### Types of Messages
- Info: General information
- Success: Completed operations
- Warning: Potential issues
- Error: Operation failures
- Progress: Operation status

### Features
1. Filtering:
   - By type
   - By source
   - By time range

2. Statistics:
   - Message distribution
   - Error rates
   - Source activity

3. Export:
   - JSON format
   - CSV format
   - System clipboard

## Configuration

### Paths
```yaml
paths:
  default_download: ~/repositories
  temp: ~/.cache/repo_tool
  logs: ~/.local/share/repo_tool/logs
```

### Display
```yaml
display:
  theme: dark  # or light, system
  show_progress: true
  show_messages: true
  message_retention_days: 7
```

### Download Options
```yaml
download:
  max_concurrent: 3
  timeout_seconds: 300
  verify_ssl: true
  allow_multiple_selection: true
```

### Services
```yaml
services:
  github:
    enabled: true
    use_gh_cli: true
    prefer_ssh: true
  gitlab:
    enabled: true
    prefer_ssh: true
  bitbucket:
    enabled: true
    prefer_ssh: true
```

## Keyboard Shortcuts

### Global
- `q`: Quit
- `h`: Help
- `s`: Settings
- `m`: Message center
- `r`: Refresh

### Repository Management
- `n`: New repository
- `f`: Fork repository
- `d`: Delete repository
- `i`: Create issue
- `c`: Cancel operation

### Message Center
- `t`: Toggle view mode
- `f`: Filter messages
- `c`: Clear messages
- `e`: Export messages

## Tips and Tricks

### Efficient Repository Selection
1. Use search to filter repositories
2. Use wildcards in search
3. Save common searches

### Batch Downloads
1. Create repository list file
2. Use relative paths for organization
3. Monitor progress in message center

### Custom Templates
1. Create repository templates
2. Store common configurations
3. Share across team

### Error Handling
1. Check message center for details
2. Export logs for troubleshooting
3. Retry failed operations

### Performance
1. Adjust concurrent downloads
2. Use SSH for faster cloning
3. Configure message retention

### Security
1. Regular PAT rotation
2. SSH key best practices
3. Secure configuration storage

