@echo off
REM Build script for Windows

echo Building coding-llm-monitor executable...

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install build dependencies
echo Installing build dependencies...
pip install -q -r requirements-build.txt

REM Install runtime dependencies
echo Installing runtime dependencies...
pip install -q -r requirements.txt

REM Build the executable
echo Building executable with PyInstaller...
pyinstaller status.spec --clean

echo.
echo Build complete! Executable is in: dist\coding-llm-monitor.exe
echo.
echo To test the executable:
echo   dist\coding-llm-monitor.exe
echo.
echo To distribute, copy the 'coding-llm-monitor.exe' file from dist\ to your target system.

pause

