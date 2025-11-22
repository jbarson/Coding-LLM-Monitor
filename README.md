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

## Testing

This project includes a comprehensive test suite with 59 tests covering all major functionality.

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=status --cov-report=html
```

See `TESTING.md` for detailed testing documentation.

## Documentation

- `QUICK_START.md` - Quick start guide for users
- `DISTRIBUTION.md` - Guide for building and distributing executables
- `TESTING.md` - Testing guide and documentation

## Requirements

- Python 3.8+ (if running from source)
- Internet connection (for status checks)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments

- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal UI
- Uses [aiohttp](https://github.com/aio-libs/aiohttp) for async HTTP requests
- Status page data from various service providers
