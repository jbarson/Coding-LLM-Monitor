# Homebrew Installation Guide

This guide explains how to make `coding-llm-monitor` available via Homebrew.

## Option 1: Create a Homebrew Tap (Recommended)

A Homebrew tap is a GitHub repository containing Homebrew formulas. This is the easiest way to distribute your app.

### Step 1: Create a Tap Repository

1. Create a new GitHub repository named `homebrew-coding-llm-monitor` (or `homebrew-tap`)
2. The repository name must start with `homebrew-`

### Step 2: Add the Formula

1. Create a `Formula` directory in the tap repository
2. Copy the formula file from this repository: `Formula/coding-llm-monitor.rb`
3. Update the SHA256 checksums (see below)
4. Commit and push to the tap repository

### Step 3: Calculate SHA256 Checksums

For each binary you release, calculate the SHA256:

```bash
# For macOS binary
shasum -a 256 dist/coding-llm-monitor-macos

# For Linux binary
shasum -a 256 dist/coding-llm-monitor-linux
```

Update the `sha256` values in the formula file.

### Step 4: Install from Tap

Users can then install with:

```bash
brew tap jbarson/coding-llm-monitor
brew install coding-llm-monitor
```

## Option 2: Submit to Homebrew Core (Advanced)

For wider distribution, you can submit to the official Homebrew core repository. This requires:

1. **Stable releases**: At least 20 GitHub stars
2. **Formula requirements**: Follow Homebrew's formula guidelines
3. **Review process**: Submit a pull request to homebrew-core

See: https://docs.brew.sh/Adding-Software-to-Homebrew

## Automated Formula Updates

You can automate formula updates by:

1. Adding a GitHub Action that updates the formula when you create a new release
2. Using tools like `brew bump-formula-pr` to automatically update versions

## Formula Template

The formula template is located at: `Formula/coding-llm-monitor.rb`

### Key Points:

- **Version**: Update when you release new versions
- **URLs**: Point to GitHub release assets
- **SHA256**: Must match the binary checksums
- **Install**: Copies binary to `bin/` directory

## Testing the Formula Locally

Before publishing, test locally:

```bash
# Install from local formula
brew install --build-from-source Formula/coding-llm-monitor.rb

# Or create a tap locally
mkdir -p ~/homebrew-tap/Formula
cp Formula/coding-llm-monitor.rb ~/homebrew-tap/Formula/
brew tap jbarson/tap ~/homebrew-tap
brew install coding-llm-monitor
```

## Updating the Formula

When releasing a new version:

1. Update the `version` in the formula
2. Update the `url` to point to the new release
3. Calculate new SHA256 checksums
4. Update the `sha256` values
5. Commit and push to the tap repository

## Example: Creating the Tap

```bash
# Create tap repository
gh repo create homebrew-coding-llm-monitor --public

# Clone it
git clone https://github.com/jbarson/homebrew-coding-llm-monitor.git
cd homebrew-coding-llm-monitor

# Create Formula directory
mkdir -p Formula

# Copy and update the formula
cp ../Coding-LLM-Monitor/Formula/coding-llm-monitor.rb Formula/

# Calculate checksums and update formula
# (Edit Formula/coding-llm-monitor.rb with correct SHA256 values)

# Commit and push
git add Formula/
git commit -m "Add coding-llm-monitor formula"
git push origin main
```

## Installation Instructions for Users

Once the tap is set up, users can install with:

```bash
brew tap jbarson/coding-llm-monitor
brew install coding-llm-monitor
```

Then run:
```bash
coding-llm-monitor
```

