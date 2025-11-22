# Coding-LLM-Monitor - Distribution Guide

This guide explains how to build and distribute the Coding-LLM-Monitor as a standalone executable.

## Building the Standalone Executable

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Build Steps

#### macOS/Linux:

```bash
# 1. Create and activate virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate

# 2. Run the build script
chmod +x build.sh
./build.sh
```

#### Windows:

```cmd
REM 1. Create and activate virtual environment (if not already done)
python -m venv venv
venv\Scripts\activate

REM 2. Run the build script
build.bat
```

### Manual Build (Alternative)

If you prefer to build manually:

```bash
# Install build dependencies
pip install -r requirements-build.txt

# Install runtime dependencies
pip install -r requirements.txt

# Build with PyInstaller
pyinstaller status.spec --clean
```

## Output

After building, you'll find the executable in the `dist/` directory:

- **macOS/Linux**: `dist/coding-llm-monitor`
- **Windows**: `dist/coding-llm-monitor.exe`

## Testing the Executable

### macOS/Linux:
```bash
./dist/coding-llm-monitor
```

### Windows:
```cmd
dist\coding-llm-monitor.exe
```

## Distribution

### Single File Distribution

The executable is a single, self-contained file that includes:
- Python interpreter
- All required dependencies
- Your application code

**To distribute:**
1. Copy the executable file from `dist/` directory
2. Share it with users (via download, USB, etc.)
3. Users can run it directly without installing Python or any dependencies

### File Size

The executable will be approximately:
- **macOS**: ~30-50 MB
- **Linux**: ~30-50 MB  
- **Windows**: ~30-50 MB

This is normal for PyInstaller executables as they bundle Python and all dependencies.

### Platform-Specific Notes

#### macOS:
- First run may require users to allow the app in System Preferences > Security & Privacy
- You may want to code-sign the executable for distribution (optional)

#### Linux:
- Executable should work on most modern Linux distributions
- May need to make it executable: `chmod +x coding-llm-monitor`

#### Windows:
- Windows Defender may flag the executable on first run (false positive)
- Users may need to click "More info" > "Run anyway"
- Consider code-signing for wider distribution (optional)

## Cross-Platform Building

To build for multiple platforms:

1. **Build on macOS** → Creates macOS executable
2. **Build on Linux** → Creates Linux executable
3. **Build on Windows** → Creates Windows executable

Or use CI/CD services like GitHub Actions to build for all platforms automatically.

## Advanced Options

### Custom Icon

To add a custom icon, edit `status.spec` and set the `icon` parameter:
```python
icon='path/to/icon.ico'  # Windows
icon='path/to/icon.icns'  # macOS
```

### Reduce File Size

To reduce executable size, you can:
- Use `--onefile` mode (already enabled)
- Exclude unused modules in `status.spec`
- Use UPX compression (already enabled)

### Debugging

If the executable doesn't work:
1. Run with `--debug` flag in PyInstaller
2. Check the console output for errors
3. Verify all dependencies are included in `hiddenimports`

## Troubleshooting

**"Executable not found" or permission errors:**
- Make sure the file exists in `dist/` directory
- On Linux/macOS: `chmod +x dist/coding-llm-monitor`

**"Module not found" errors:**
- Add missing modules to `hiddenimports` in `status.spec`
- Rebuild the executable

**Large file size:**
- This is normal for PyInstaller executables
- Consider using Docker for distribution if size is a concern

**Antivirus warnings:**
- Common with PyInstaller executables
- Consider code-signing for production distribution

