# Coding-LLM-Monitor

A terminal-based dashboard for monitoring the status of code assistant services in real-time.

## Features

- ✅ Real-time status monitoring of code assistant services
- ✅ Automatic refresh every 10 minutes
- ✅ Interactive keyboard navigation
- ✅ One-click access to status pages
- ✅ Beautiful terminal UI with emoji status indicators
- ✅ Self-contained executable (no Python installation needed)

## Supported Services

- GitHub Copilot
- Cursor
- Claude Code
- Gemini Code Assist (GCP)

## Quick Start

### Option 1: Run the Executable (Recommended)

1. Download the `coding-llm-monitor` executable (or `coding-llm-monitor.exe` on Windows)
2. Open Terminal/Command Prompt
3. Run: `./coding-llm-monitor` (macOS/Linux) or `coding-llm-monitor.exe` (Windows)

### Option 2: Run from Source

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python status.py
```

## Controls

- **↑/↓ Arrow Keys**: Navigate between services
- **Enter**: Open selected service's status page in browser
- **Q**: Quit the application
- **Ctrl+C**: Force quit (if needed)

## Building the Executable

To create a standalone executable for distribution:

```bash
# macOS/Linux
./build.sh

# Windows
build.bat
```

See `DISTRIBUTION.md` for detailed build instructions.

## Status Indicators

- ✅ **Green**: Operational/Available
- ⚠️ **Yellow**: Degraded Performance
- ❌ **Red**: Major Outage/Error
- 🔧 **Cyan**: Maintenance
- ❓ **Grey**: Unknown

## Documentation

- `QUICK_START.md` - Quick start guide for users
- `DISTRIBUTION.md` - Guide for building and distributing executables

## Requirements

- Python 3.8+ (if running from source)
- Internet connection (for status checks)

## License

This project is provided as-is for personal use.
