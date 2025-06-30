#!/bin/bash
set -euo pipefail

# Setup script for security implementation

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
chmod 750 logs

# Create SSH directory if it doesn't exist
if [ ! -d ~/.ssh ]; then
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
fi

# Check if the security configuration exists
if [ ! -f security_config.yaml ]; then
    echo "Error: security_config.yaml not found!"
    exit 1
fi

# Setup Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}"

echo "Security setup completed successfully!"
echo "Make sure to review security_config.yaml and adjust settings as needed."

