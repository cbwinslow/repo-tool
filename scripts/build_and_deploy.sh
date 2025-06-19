#!/bin/bash

# Build and deployment script for RepoTool
# This script automates the build and deployment process

set -e  # Exit on error

# Configuration
VERSION=$(grep -m1 "VERSION = " Makefile | cut -d'"' -f2)
NAME="repo-tool"
DOCKER_REGISTRY="ghcr.io"
DOCKER_REPO="cbwinslow/repo-tool"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check requirements
check_requirements() {
    log "Checking requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        error "Node.js is required but not installed."
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        warn "Docker is not installed. Docker build will be skipped."
    fi
    
    # Check build tools
    if ! command -v make &> /dev/null; then
        error "Make is required but not installed."
        exit 1
    fi
}

# Setup environment
setup_environment() {
    log "Setting up environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -e ".[dev]"
    npm install
}

# Run tests
run_tests() {
    log "Running tests..."
    
    # Run Python tests
    pytest tests/
    
    # Run TypeScript tests
    npm test
}

# Build packages
build_packages() {
    log "Building packages..."
    
    # Clean previous builds
    make clean
    
    # Build Python package
    python -m build
    
    # Build DEB package
    make deb
    
    # Build Snap package
    if command -v snapcraft &> /dev/null; then
        make snap
    else
        warn "Snapcraft not installed. Snap package build skipped."
    fi
    
    # Build Flatpak package
    if command -v flatpak-builder &> /dev/null; then
        make flatpak
    else
        warn "Flatpak builder not installed. Flatpak build skipped."
    fi
    
    # Build Docker image
    if command -v docker &> /dev/null; then
        make docker
    fi
}

# Run security checks
security_checks() {
    log "Running security checks..."
    
    # Run Bandit for Python security checks
    if command -v bandit &> /dev/null; then
        bandit -r src/
    else
        warn "Bandit not installed. Python security check skipped."
    fi
    
    # Run npm audit
    npm audit
    
    # Run Snyk if available
    if command -v snyk &> /dev/null; then
        snyk test
    else
        warn "Snyk not installed. Vulnerability scan skipped."
    fi
}

# Deploy packages
deploy_packages() {
    log "Deploying packages..."
    
    # Create release directory
    mkdir -p dist/release
    
    # Copy artifacts
    cp dist/*.whl dist/release/
    cp dist/*.tar.gz dist/release/
    cp dist/*.deb dist/release/
    [ -f dist/*.snap ] && cp dist/*.snap dist/release/
    [ -f dist/*.flatpak ] && cp dist/*.flatpak dist/release/
    
    # Generate checksums
    cd dist/release
    sha256sum * > SHA256SUMS
    cd ../..
    
    # Push Docker image if credentials available
    if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
        docker push ${DOCKER_REGISTRY}/${DOCKER_REPO}:latest
        docker push ${DOCKER_REGISTRY}/${DOCKER_REPO}:${VERSION}
    else
        warn "Docker credentials not found. Image push skipped."
    fi
}

# Cleanup function
cleanup() {
    log "Cleaning up..."
    deactivate || true
}

# Main execution
main() {
    log "Starting build and deployment process for ${NAME} v${VERSION}"
    
    # Register cleanup
    trap cleanup EXIT
    
    # Run steps
    check_requirements
    setup_environment
    run_tests
    security_checks
    build_packages
    deploy_packages
    
    log "Build and deployment completed successfully!"
}

# Run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

