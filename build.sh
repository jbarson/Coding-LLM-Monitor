#!/bin/bash
# Build script for creating standalone executable

set -e

echo "Building coding-llm-monitor executable..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install build dependencies
echo "Installing build dependencies..."
pip install -q -r requirements-build.txt

# Install runtime dependencies
echo "Installing runtime dependencies..."
pip install -q -r requirements.txt

# Build the executable
echo "Building executable with PyInstaller..."
pyinstaller status.spec --clean

echo ""
echo "Build complete! Executable is in: dist/coding-llm-monitor"
echo ""
echo "To test the executable:"
echo "  ./dist/coding-llm-monitor"
echo ""
echo "To distribute, copy the 'coding-llm-monitor' file from dist/ to your target system."

