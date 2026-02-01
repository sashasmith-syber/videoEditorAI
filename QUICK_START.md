# Quick Start Guide

## To Run the Desktop App

The desktop application requires **V Language** to be installed first.

### Install V Language

**Windows:**
1. Download V from: https://vlang.io
2. Extract to a folder (e.g., `C:\v`)
3. Add V to PATH:
   - Open System Properties → Environment Variables
   - Add `C:\v` to PATH
   - Or run: `setx PATH "%PATH%;C:\v"` in Command Prompt (as Admin)

**Alternative (Chocolatey):**
```powershell
choco install vlang
```

**Verify Installation:**
```bash
v version
```

### Install FFmpeg

**Windows (Chocolatey):**
```powershell
choco install ffmpeg
```

**Or download from:** https://ffmpeg.org/download.html

**Verify:**
```bash
ffmpeg -version
```

### Build and Run

```bash
cd vfiles
v desktop_app.v
desktop_app.exe
```

Or use the build script:
```bash
build_desktop.bat
```

---

## Alternative: Use Python Version (Temporary)

If you need to use the app immediately while setting up V:

```bash
python autoedit.py -input <folder> -output <output_folder>
```

See `autoedit.py` for available options.
