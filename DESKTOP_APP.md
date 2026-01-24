# Video Editor AI - Desktop Application

## Overview

This desktop application provides a graphical user interface for the Video Editor AI project, allowing users to automatically process videos with minimal interaction.

## Features

- **File Selection**: Select individual video files or entire folders
- **Audio Extraction**: Automatically extract all audio tracks from videos
- **Format Options**: Choose output formats for video (mp4, mkv, avi, mov) and audio (mp3, m4a, wav, ogg)
- **Audio Combining**: Option to combine all audio tracks into a single track
- **Progress Tracking**: Real-time progress bar and status updates
- **Cross-Platform**: Works on Windows, Linux, and macOS

## Requirements

1. **V Programming Language**: Install V from [vlang.io](https://vlang.io)
2. **FFmpeg**: Required for video processing
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `choco install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (RHEL/CentOS)
   - macOS: `brew install ffmpeg`

3. **V UI Library**: The application uses V's built-in UI library

## Building

### Windows
```bash
cd vfiles
v desktop_app.v
```

### Linux/macOS
```bash
cd vfiles
v desktop_app.v
```

## Running

After building, run the executable:
- Windows: `desktop_app.exe`
- Linux/macOS: `./desktop_app`

## Usage

1. **Select Videos**: 
   - Click "Select Video Files" to choose individual files
   - Click "Select Folder" to process all videos in a folder

2. **Configure Settings**:
   - Set output directory (default: `output` folder in current directory)
   - Choose video format (mp4, mkv, avi, mov)
   - Choose audio format (mp3, m4a, wav, ogg)
   - Optionally enable "Combine all audio tracks"

3. **Process**:
   - Click "Start Processing" to begin
   - Monitor progress in the progress bar
   - Click "Stop" to cancel processing

## Output Structure

```
output/
├── audio/
│   ├── video1-track-0.wav
│   ├── video1-track-1.wav
│   └── video1-combined.wav (if combine_audio is enabled)
└── clips/
    └── (future: silence-cut clips)
```

## Troubleshooting

### FFmpeg Not Found
- Ensure FFmpeg is installed and available in your system PATH
- Test by running `ffmpeg -version` in terminal/command prompt

### File Dialog Not Working
- Windows: Requires PowerShell (usually pre-installed)
- Linux: Install zenity: `sudo apt-get install zenity`
- macOS: Should work out of the box

### UI Library Issues
If V's UI library is not available, you can:
1. Install V UI: `v install ui` (if using V package manager)
2. Use the command-line version: `v run videoeditor.v`

## Development

### Project Structure
```
vfiles/
├── desktop_app.v          # Main GUI application
├── src/
│   └── desktop/
│       ├── file_manager.v    # File/folder selection
│       └── video_processor.v  # FFmpeg video processing
└── v.mod                  # Module definition
```

### Adding Features

To add new features:
1. Add UI components in `desktop_app.v`
2. Implement processing logic in `video_processor.v`
3. Update file handling in `file_manager.v` if needed

## License

GPL-3.0-or-later (same as main project)
