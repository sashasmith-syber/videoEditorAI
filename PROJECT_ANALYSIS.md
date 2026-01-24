# Video Editor AI - Project Analysis & Desktop App

## Project Overview

**Video Editor AI** is an automatic video editing application that processes videos with minimal human interaction. The project is currently being migrated from Python to V language.

### Current Status
- ✅ Audio track extraction from videos
- 🚧 Video cutting by silence (planned)
- ✅ Desktop GUI application (newly added)

## Project Structure

```
videoEditorAI/
├── vfiles/                    # V language source code
│   ├── desktop_app.v         # Main desktop GUI application ⭐ NEW
│   ├── videoEditorAI.v       # Simple CLI entry point
│   ├── videoeditor.v         # CLI argument parsing
│   ├── src/
│   │   ├── src.v             # Core module
│   │   ├── argparse/
│   │   │   └── args.v       # Argument parser (incomplete)
│   │   ├── video/
│   │   │   └── cut.v        # Video cutting functions
│   │   └── desktop/         # Desktop app modules ⭐ NEW
│   │       ├── file_manager.v      # File/folder selection
│   │       └── video_processor.v    # FFmpeg video processing
│   └── v.mod                 # Module definition
├── autoedit.py               # Original Python implementation
├── README.md                 # Project documentation
├── DESKTOP_APP.md           # Desktop app guide ⭐ NEW
├── BUILD.md                 # Build instructions ⭐ NEW
├── build_desktop.bat        # Windows build script ⭐ NEW
└── build_desktop.sh         # Linux/macOS build script ⭐ NEW
```

## Desktop Application Features

### ✅ Implemented Features

1. **Graphical User Interface**
   - Modern, clean UI with grouped sections
   - Real-time status updates
   - Progress bar for processing

2. **File Management**
   - Select individual video files (native file dialog)
   - Select entire folders for batch processing
   - Cross-platform file dialogs (Windows/Linux/macOS)

3. **Video Processing**
   - Extract all audio tracks from videos
   - Support for multiple video formats (mp4, mkv, avi, mov)
   - Support for multiple audio formats (mp3, m4a, wav, ogg)
   - Option to combine all audio tracks into one

4. **Settings & Configuration**
   - Customizable output directory
   - Video format selection
   - Audio format selection
   - Audio combining toggle

5. **Progress Tracking**
   - Real-time progress bar
   - Status messages
   - File-by-file processing feedback

### 🔧 Technical Implementation

#### Core Technologies
- **V Language**: Main programming language
- **V UI Library**: Cross-platform GUI framework
- **FFmpeg**: Video/audio processing backend
- **FFprobe**: Video analysis tool

#### Architecture
- **Modular Design**: Separated concerns (UI, file management, video processing)
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Native Dialogs**: Platform-specific file/folder selection
- **Async Processing**: Non-blocking video processing

#### Key Modules

1. **desktop_app.v**
   - Main application entry point
   - UI layout and components
   - Event handlers
   - State management

2. **file_manager.v**
   - Native file/folder dialogs
   - Video file detection
   - Folder scanning

3. **video_processor.v**
   - FFmpeg command generation
   - Audio track extraction
   - Audio combining
   - FFmpeg availability checking

## Comparison: Python vs V Implementation

### Python (autoedit.py)
- ✅ Working audio extraction
- ✅ Command-line interface
- ✅ Basic argument parsing
- ❌ No GUI
- ❌ Limited error handling

### V (desktop_app.v)
- ✅ Desktop GUI application
- ✅ Cross-platform file dialogs
- ✅ Progress tracking
- ✅ Better error handling
- ✅ Modular architecture
- 🚧 Audio extraction (implemented, needs testing)
- 🚧 Video cutting by silence (planned)

## Dependencies

### Required
- **V Language** (v0.4+)
- **FFmpeg** (with ffprobe)

### Optional
- **zenity** (Linux - for file dialogs)
- **PowerShell** (Windows - usually pre-installed)

## Build & Run

### Quick Start
```bash
# Windows
build_desktop.bat

# Linux/macOS
chmod +x build_desktop.sh
./build_desktop.sh
```

### Manual Build
```bash
cd vfiles
v desktop_app.v
```

## Usage Workflow

1. **Launch Application**: Run `desktop_app.exe` (or `./desktop_app`)
2. **Select Videos**: Use "Select Video Files" or "Select Folder"
3. **Configure**: Set output directory and formats
4. **Process**: Click "Start Processing"
5. **Monitor**: Watch progress bar and status messages
6. **Results**: Check `output/audio/` folder for extracted tracks

## Future Enhancements

### Planned Features
- [ ] Video cutting by silence detection
- [ ] Preview video thumbnails
- [ ] Batch processing queue
- [ ] Export final edited videos
- [ ] Audio normalization
- [ ] Video trimming interface
- [ ] Settings persistence

### Technical Improvements
- [ ] Better error handling and user feedback
- [ ] Progress cancellation
- [ ] Multi-threaded processing
- [ ] Configuration file support
- [ ] Logging system

## Known Limitations

1. **UI Library**: V's UI library is still evolving - API may change
2. **File Dialogs**: Some platforms may need additional tools (zenity on Linux)
3. **FFmpeg**: Must be installed and in PATH
4. **Large Files**: Processing large videos may take time (no cancellation yet)

## Testing Checklist

- [ ] Build on Windows
- [ ] Build on Linux
- [ ] Build on macOS
- [ ] File selection works
- [ ] Folder selection works
- [ ] Audio extraction works
- [ ] Progress bar updates
- [ ] Error handling works
- [ ] FFmpeg detection works

## Contributing

The project is open to contributions. Areas that need work:
- Video cutting by silence
- Better error messages
- UI improvements
- Cross-platform testing
- Documentation

## License

GPL-3.0-or-later
