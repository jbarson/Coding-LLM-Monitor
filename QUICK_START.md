# Coding-LLM-Monitor - Quick Start

## For End Users (Running the Executable)

### Download and Run

1. **Download** the `coding-llm-monitor` executable (or `coding-llm-monitor.exe` on Windows)
2. **Open Terminal** (macOS/Linux) or **Command Prompt** (Windows)
3. **Navigate** to where you downloaded the file
4. **Run** the executable:
   - macOS/Linux: `./coding-llm-monitor`
   - Windows: `coding-llm-monitor.exe`

That's it! The dashboard will start and show the status of code assistant services.

### Controls

- **↑/↓ Arrow Keys**: Navigate between services
- **Enter**: Open selected service's status page in browser
- **Q**: Quit the application
- **Ctrl+C**: Force quit (if needed)

## For Developers (Building from Source)

### Prerequisites

- Python 3.8+
- pip

### Setup

```bash
# 1. Clone or download the project
# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python status.py
```

### Building Executable

See `DISTRIBUTION.md` for detailed build instructions.

Quick build:
```bash
./build.sh  # macOS/Linux
# or
build.bat   # Windows
```

## Features

- ✅ Real-time status monitoring of code assistant services
- ✅ Automatic refresh every 10 minutes
- ✅ Interactive keyboard navigation
- ✅ One-click access to status pages
- ✅ Beautiful terminal UI with emoji status indicators

## Supported Services

- GitHub Copilot
- Cursor
- Claude Code
- Gemini Code Assist (GCP)

## Troubleshooting

**Executable won't run:**
- Make sure it has execute permissions: `chmod +x coding-llm-monitor`
- Check your terminal/command prompt is in the right directory

**No status updates:**
- Check your internet connection
- Some services may be temporarily unavailable

**Keyboard navigation not working:**
- This feature works on macOS/Linux terminals
- On Windows, you can still view status (refresh happens automatically)

