#!/bin/bash

# Automation script for RepoTool
# This script automates common development and maintenance tasks

set -e  # Exit on error

# Configuration
VERSION=$(grep -m1 "VERSION = " Makefile | cut -d'"' -f2)
NAME="repo-tool"
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Development environment setup
setup_dev() {
    log "Setting up development environment..."
    
    # Create virtual environment
    python3 -m venv .venv
    source .venv/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -e ".[dev]"
    npm install
    
    # Install pre-commit hooks
    pre-commit install
    
    # Configure git hooks
    git config core.hooksPath .github/hooks
    
    log "Development environment setup complete"
}

# Release management
create_release() {
    local version="$1"
    local branch="release/${version}"
    
    log "Creating release ${version}..."
    
    # Create release branch
    git checkout -b "${branch}"
    
    # Update version
    sed -i "s/VERSION = .*/VERSION = \"${version}\"/" Makefile
    
    # Update changelog
    # Generate changelog
    "${SCRIPTS_DIR}/generate_changelog.sh"
    
    # Create commit
    git add Makefile CHANGELOG.md
    git commit -m "Release ${version}"
    
    # Create tag
    git tag -a "v${version}" -m "Version ${version}"
    
    # Push changes
    git push origin "${branch}"
    git push origin "v${version}"
    
    log "Release ${version} created"
}

# Documentation generation
generate_docs() {
    log "Generating documentation..."
    
    # Generate API documentation
    sphinx-apidoc -f -o docs/source/api src/repo_tool
    
    # Build documentation
    cd docs && make html
    cd ..
    
    log "Documentation generated in docs/build/html"
}

# Quality checks
run_quality_checks() {
    log "Running quality checks..."
    
    # Run linters
    flake8 src/ tests/
    mypy src/ tests/
    black --check src/ tests/
    npm run lint
    
    # Run tests in parallel
    pytest tests/ -n auto --dist loadfile
    npm test -- --parallel
    
    # Run security scan
    "${SCRIPTS_DIR}/security_scan.sh"
    
    log "Quality checks completed"
}

# Dependency updates
update_dependencies() {
    log "Updating dependencies..."
    
    # Update Python dependencies
    pip install --upgrade pip
    pip list --outdated --format=json | \
        jq -r '.[] | select(.name != "pip") | .name' | \
        xargs -I {} pip install --upgrade {}
    
    # Update npm dependencies
    npm update
    
    # Generate requirements.txt
    pip freeze > requirements.txt
    
    # Create branch for updates
    git checkout -b "deps/update-$(date +%Y%m%d)"
    git add requirements.txt package.json
    git commit -m "Update dependencies"
    git push origin "deps/update-$(date +%Y%m%d)"
    
    log "Dependencies updated"
}

# System maintenance
run_maintenance() {
    log "Running system maintenance..."
    
    # Clean Python cache
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    find . -type d -name ".pytest_cache" -delete
    
    # Clean npm cache
    npm cache clean --force
    
    # Clean build artifacts
    rm -rf build/ dist/ *.egg-info/
    
    # Optimize database
    if [ -f ~/.local/share/repo_tool/messages.db ]; then
        sqlite3 ~/.local/share/repo_tool/messages.db "VACUUM;"
    fi
    
    # Rotate logs
    find ~/.local/share/repo_tool/logs -name "*.log.*" -mtime +30 -delete
    
    log "Maintenance completed"
}

# Performance profiling
run_profiling() {
    log "Running performance profiling..."
    
    # Create profiling directory
    mkdir -p reports/profiling
    
    # Run Python profiling
    python -m cProfile -o reports/profiling/profile.stats src/repo_tool/__main__.py
    python -c "import pstats; p = pstats.Stats('reports/profiling/profile.stats'); p.sort_stats('cumulative').print_stats(50)"
    
    # Run memory profiling
    mprof run src/repo_tool/__main__.py
    mprof plot
    
    log "Profiling completed. Results in reports/profiling/"
}

# Container management
manage_containers() {
    log "Managing containers..."
    
    # Build container
    docker build -t "ghcr.io/cbwinslow/${NAME}:${VERSION}" .
    
    # Run tests in container
    docker run --rm "ghcr.io/cbwinslow/${NAME}:${VERSION}" pytest
    
    # Push container
    docker push "ghcr.io/cbwinslow/${NAME}:${VERSION}"
    
    log "Container management completed"
}

# Project initialization
init_project() {
    log "Initializing new project..."
    
    # Create directory structure
    mkdir -p src/repo_tool/{core,tui,data}
    mkdir -p tests/{unit,integration,benchmarks}
    mkdir -p docs/{source,build}
    mkdir -p scripts
    mkdir -p .github/{workflows,hooks}
    
    # Create initial files
    touch src/repo_tool/__init__.py
    touch tests/__init__.py
    
    # Initialize git
    git init
    git add .
    git commit -m "Initial commit"
    
    log "Project initialized"
}

# Usage information
usage() {
    echo "Usage: $0 <command> [options]"
    echo
    echo "Commands:"
    echo "  setup          Setup development environment"
    echo "  release        Create a new release"
    echo "  docs           Generate documentation"
    echo "  quality        Run quality checks"
    echo "  update         Update dependencies"
    echo "  maintain       Run system maintenance"
    echo "  profile        Run performance profiling"
    echo "  containers     Manage containers"
    echo "  init          Initialize new project"
    echo
    echo "Options:"
    echo "  -v, --version    Specify version for release"
    echo "  -h, --help       Show this help message"
}

# Parse command line arguments
COMMAND=""
VERSION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        setup|release|docs|quality|update|maintain|profile|containers|init)
            COMMAND="$1"
            shift
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            error "Unknown argument: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate input
if [ -z "${COMMAND}" ]; then
    error "No command specified"
    usage
    exit 1
fi

# Execute command
case "${COMMAND}" in
    setup)
        setup_dev
        ;;
    release)
        if [ -z "${VERSION}" ]; then
            error "Version required for release"
            exit 1
        fi
        create_release "${VERSION}"
        ;;
    docs)
        generate_docs
        ;;
    quality)
        run_quality_checks
        ;;
    update)
        update_dependencies
        ;;
    maintain)
        run_maintenance
        ;;
    profile)
        run_profiling
        ;;
    containers)
        manage_containers
        ;;
    init)
        init_project
        ;;
    *)
        error "Unknown command: ${COMMAND}"
        usage
        exit 1
        ;;
esac

