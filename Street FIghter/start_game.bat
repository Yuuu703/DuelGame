@echo off
title Street Fighter LAN Game
echo.
echo ================================================
echo           Street Fighter LAN Game
echo ================================================
echo.
echo Starting game launcher...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Try to run with Python
python launcher.py
if %ERRORLEVEL% EQU 0 goto end

REM If that fails, try python3
python3 launcher.py
if %ERRORLEVEL% EQU 0 goto end

REM If both fail, try py command
py launcher.py
if %ERRORLEVEL% EQU 0 goto end

REM If all fail, show error
echo.
echo ERROR: Python is not installed or not in PATH
echo Please install Python 3.x and make sure it's in your PATH
echo.
echo You can also try running the game directly:
echo   python main.py
echo   or
echo   python3 main.py
echo.

:end
echo.
echo Press any key to exit...
pause >nul
