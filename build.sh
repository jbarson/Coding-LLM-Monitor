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

# Detect OS and create platform-specific binary name
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM_NAME="coding-llm-monitor-macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM_NAME="coding-llm-monitor-linux"
else
    PLATFORM_NAME="coding-llm-monitor"
fi

# Copy to platform-specific name
cp dist/coding-llm-monitor "dist/${PLATFORM_NAME}"
chmod +x "dist/${PLATFORM_NAME}"

echo ""
echo "Build complete! Executables available:"
echo "  - dist/coding-llm-monitor (generic name)"
echo "  - dist/${PLATFORM_NAME} (platform-specific name)"
echo ""
echo "To test the executable:"
echo "  ./dist/coding-llm-monitor"
echo ""
echo "To distribute, copy the '${PLATFORM_NAME}' file from dist/ to your target system."

