@echo off
echo Building Video Editor AI Desktop Application...
echo.

cd vfiles

echo Checking V installation...
v version
if %errorlevel% neq 0 (
    echo ERROR: V is not installed or not in PATH
    echo Please install V from https://vlang.io
    pause
    exit /b 1
)

echo.
echo Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: FFmpeg not found in PATH
    echo The application requires FFmpeg to process videos
    echo Please install FFmpeg from https://ffmpeg.org
    echo.
)

echo.
echo Building desktop application...
v desktop_app.v

if %errorlevel% equ 0 (
    echo.
    echo Build successful!
    echo Run desktop_app.exe to start the application
) else (
    echo.
    echo Build failed. Please check the error messages above.
)

pause
