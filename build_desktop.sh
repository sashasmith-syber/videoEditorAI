#!/bin/bash

echo "Building Video Editor AI Desktop Application..."
echo ""

cd vfiles

echo "Checking V installation..."
if ! command -v v &> /dev/null; then
    echo "ERROR: V is not installed or not in PATH"
    echo "Please install V from https://vlang.io"
    exit 1
fi

v version
echo ""

echo "Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "WARNING: FFmpeg not found in PATH"
    echo "The application requires FFmpeg to process videos"
    echo "Please install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo ""
fi

echo "Building desktop application..."
v desktop_app.v

if [ $? -eq 0 ]; then
    echo ""
    echo "Build successful!"
    echo "Run ./desktop_app to start the application"
else
    echo ""
    echo "Build failed. Please check the error messages above."
    exit 1
fi
