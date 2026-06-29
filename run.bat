@echo off
chcp 65001 >nul
title ProokSuite Pro

echo ================================================
echo    ProokSuite Pro - Advanced Modding Tool
echo ================================================
echo.

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org
    pause
    exit /b 1
)

echo [INFO] Installing required packages...
pip install --quiet PyQt6 psutil pycryptodome 2>nul

echo [INFO] Starting ProokSuite Pro...
python app/main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application crashed. Check logs/ folder for details.
    pause
)