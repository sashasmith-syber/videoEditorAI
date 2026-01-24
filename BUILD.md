# Build Instructions

## Quick Start

1. **Install V Language**
   ```bash
   # Visit https://vlang.io and follow installation instructions
   # Or use package manager:
   # Windows: choco install vlang
   # Linux: See vlang.io installation guide
   # macOS: brew install vlang
   ```

2. **Install FFmpeg**
   ```bash
   # Windows
   choco install ffmpeg
   # OR download from https://ffmpeg.org
   
   # Linux (Ubuntu/Debian)
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   ```

3. **Build Desktop App**
   ```bash
   cd vfiles
   v desktop_app.v
   ```

4. **Run**
   ```bash
   # Windows
   desktop_app.exe
   
   # Linux/macOS
   ./desktop_app
   ```

## Alternative: Command Line Version

If you prefer command-line interface or UI library is not available:

```bash
cd vfiles
v run videoeditor.v --help
```

## Development Build

For development with auto-reload:

```bash
cd vfiles
v watch desktop_app.v
```

## Troubleshooting

### V UI Library Not Found
V's UI library should be included with V. If you encounter issues:
- Update V to latest version: `v up`
- Check V installation: `v version`

### FFmpeg Path Issues
- Ensure FFmpeg is in system PATH
- Test: `ffmpeg -version` should work
- Windows: Add FFmpeg bin directory to PATH environment variable

### Compilation Errors
- Ensure you're using V 0.4+ (UI support)
- Check module paths match directory structure
- Verify all dependencies are available
