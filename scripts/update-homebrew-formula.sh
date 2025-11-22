#!/bin/bash
# Script to update Homebrew formula with new release information

set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.0.1"
    exit 1
fi

FORMULA_FILE="Formula/coding-llm-monitor.rb"
TAG="v${VERSION}"

echo "Updating Homebrew formula for version ${VERSION}..."

# Check if formula file exists
if [ ! -f "$FORMULA_FILE" ]; then
    echo "Error: Formula file not found at $FORMULA_FILE"
    exit 1
fi

# Update version in formula
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/version \".*\"/version \"${VERSION}\"/" "$FORMULA_FILE"
else
    # Linux
    sed -i "s/version \".*\"/version \"${VERSION}\"/" "$FORMULA_FILE"
fi

# Update URLs
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|releases/download/v[0-9.]*/|releases/download/${TAG}/|g" "$FORMULA_FILE"
else
    sed -i "s|releases/download/v[0-9.]*/|releases/download/${TAG}/|g" "$FORMULA_FILE"
fi

echo "Formula updated to version ${VERSION}"
echo ""
echo "Next steps:"
echo "1. Calculate SHA256 checksums for the binaries:"
echo "   shasum -a 256 dist/coding-llm-monitor-macos"
echo "   shasum -a 256 dist/coding-llm-monitor-linux"
echo ""
echo "2. Update the sha256 values in $FORMULA_FILE"
echo ""
echo "3. Commit and push to your Homebrew tap repository"

