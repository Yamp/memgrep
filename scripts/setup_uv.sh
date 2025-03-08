#!/bin/bash
# Script to install UV and set up the project with it

set -e  # Exit on error

echo "Installing UV package manager..."

# Install UV
curl -sSf https://astral.sh/uv/install.sh | sh

# Add UV to PATH if not already there
if ! command -v uv &> /dev/null; then
    echo "Adding UV to PATH..."
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "Creating virtual environment with UV..."
uv venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies with UV..."
uv pip install -r requirements-uv.txt

echo "Setup complete! You can now use UV for package management."
echo "To activate the virtual environment, run: source .venv/bin/activate"