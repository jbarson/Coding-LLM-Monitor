#!/bin/bash
# Script to create a Homebrew tap repository

set -e

TAP_NAME="homebrew-coding-llm-monitor"
GITHUB_USER="jbarson"

echo "Creating Homebrew tap: ${TAP_NAME}..."

# Create the tap repository
gh repo create "${TAP_NAME}" --public --description "Homebrew tap for Coding-LLM-Monitor"

# Clone it
git clone "https://github.com/${GITHUB_USER}/${TAP_NAME}.git" /tmp/${TAP_NAME}
cd /tmp/${TAP_NAME}

# Create Formula directory
mkdir -p Formula

# Copy the formula
cp "$(git rev-parse --show-toplevel)/Formula/coding-llm-monitor.rb" Formula/

# Initial commit
git add Formula/
git commit -m "Add coding-llm-monitor formula"
git push origin main

echo ""
echo "✅ Homebrew tap created!"
echo ""
echo "Users can now install with:"
echo "  brew tap ${GITHUB_USER}/${TAP_NAME}"
echo "  brew install coding-llm-monitor"
echo ""
echo "Don't forget to:"
echo "1. Calculate SHA256 checksums for your binaries"
echo "2. Update the formula with correct checksums"
echo "3. Commit and push the updates"
