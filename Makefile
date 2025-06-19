.PHONY: build test install clean lint docs deb snap flatpak docker release

# Python virtual environment
VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
NPM = npm

# Build configuration
NAME = repo-tool
VERSION = 1.0.0
ARCH = amd64
MAINTAINER = "Blaine Winslow <blaine.winslow@gmail.com>"

# Directories
BUILD_DIR = build
DIST_DIR = dist
DEB_DIR = $(BUILD_DIR)/deb
SNAP_DIR = $(BUILD_DIR)/snap
FLATPAK_DIR = $(BUILD_DIR)/flatpak

# Docker configuration
DOCKER_REGISTRY = ghcr.io
DOCKER_REPO = cbwinslow/repo-tool
DOCKER_TAG = latest

# Default target
all: build

$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

# Build both Python and TypeScript components
build: $(VENV)
	$(PIP) install -e .
	$(NPM) install
	$(NPM) run build

# Run all tests
test: $(VENV)
	$(PYTHON) -m pytest tests/
	$(NPM) test

# Install the package
install: build
	$(PIP) install -e .
	$(NPM) install

# Clean build artifacts and temporary files
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf $(VENV)
	rm -rf node_modules/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete

# Lint code
lint: $(VENV)
	$(PYTHON) -m flake8 src/ tests/
	$(PYTHON) -m mypy src/ tests/
	$(NPM) run lint

# Generate documentation
docs: $(VENV)
	$(PYTHON) -m sphinx-build -b html docs/source/ docs/build/html

# Package building targets
deb: $(VENV)
	# Create DEB package structure
	mkdir -p $(DEB_DIR)/DEBIAN
	mkdir -p $(DEB_DIR)/usr/bin
	mkdir -p $(DEB_DIR)/usr/lib/$(NAME)
	mkdir -p $(DEB_DIR)/usr/share/doc/$(NAME)

	# Copy files
	cp -r src/* $(DEB_DIR)/usr/lib/$(NAME)/
	cp debian/control $(DEB_DIR)/DEBIAN/
	cp debian/copyright $(DEB_DIR)/usr/share/doc/$(NAME)/
	cp README.md $(DEB_DIR)/usr/share/doc/$(NAME)/

	# Create control file
	sed -i 's/{{VERSION}}/$(VERSION)/g' $(DEB_DIR)/DEBIAN/control
	sed -i 's/{{ARCH}}/$(ARCH)/g' $(DEB_DIR)/DEBIAN/control
	sed -i 's/{{MAINTAINER}}/$(MAINTAINER)/g' $(DEB_DIR)/DEBIAN/control

	# Build package
	dpkg-deb --build $(DEB_DIR) $(DIST_DIR)/$(NAME)_$(VERSION)_$(ARCH).deb

# Snap package
snap:
	snapcraft clean
	snapcraft
	mv *.snap $(DIST_DIR)/

# Flatpak package
flatpak:
	flatpak-builder --force-clean $(FLATPAK_DIR) com.repotool.RepoTool.yaml
	flatpak build-bundle $(FLATPAK_DIR) $(DIST_DIR)/$(NAME).flatpak com.repotool.RepoTool

# Docker image
docker:
	docker build -t $(DOCKER_REGISTRY)/$(DOCKER_REPO):$(DOCKER_TAG) .

# Release
release: clean build test deb snap flatpak docker
	# Create release directory
	mkdir -p $(DIST_DIR)/release
	# Copy artifacts
	cp $(DIST_DIR)/*.deb $(DIST_DIR)/release/
	cp $(DIST_DIR)/*.snap $(DIST_DIR)/release/
	cp $(DIST_DIR)/*.flatpak $(DIST_DIR)/release/
	# Create checksums
	cd $(DIST_DIR)/release && sha256sum * > SHA256SUMS

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf $(VENV)
	rm -rf node_modules/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete

# Initialize development environment
dev-setup: $(VENV)
	# Install pre-commit hooks
	pre-commit install
	# Setup git hooks
	git config core.hooksPath .github/hooks
	# Install development tools
	$(PIP) install -e ".[dev]"
	$(NPM) install

# Run development environment
dev: $(VENV)
	$(PYTHON) -m repo_tool

# Update dependencies
update-deps: $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -e ".[dev]"
	$(NPM) update

