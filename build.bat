@echo off
setlocal enabledelayedexpansion

echo Building Pink Voice.exe (Windows)
echo.

REM Check uv installed
where uv >nul 2>&1
if errorlevel 1 (
    echo ERROR: uv not found
    echo.
    echo Install uv:
    echo   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo.
    exit /b 1
)

REM Sync dependencies (creates venv + installs)
echo Syncing dependencies...
uv sync

REM Install pyinstaller
echo Installing PyInstaller...
uv pip install pyinstaller

REM Clean previous build
echo Cleaning previous build...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build .exe
echo Building .exe...
uv run pyinstaller PinkVoiceWindows.spec

echo.
echo Build complete!
echo.
echo Output: dist\Pink Voice.exe
echo.
echo Copying to Desktop...
copy /Y "dist\Pink Voice.exe" "%USERPROFILE%\Desktop\Pink Voice.exe" >nul
echo.
echo To run:
echo   "Desktop\Pink Voice.exe"
echo.
echo With VERBOSE mode:
echo   set VERBOSE=1 ^&^& "Desktop\Pink Voice.exe"
echo.
