#!/usr/bin/env python3
"""
Video Editor AI - Desktop Application
Automatic video editing with minimal interaction.
"""

import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Video/audio format options
VIDEO_FORMATS = ["mp4", "mkv", "avi", "mov"]
AUDIO_FORMATS = ["mp3", "m4a", "wav", "ogg"]
VIDEO_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v")


def get_audio_track_count(video_path: str) -> int:
    """Get number of audio tracks using ffprobe."""
    try:
        cmd = [
            "ffprobe", "-loglevel", "error",
            "-select_streams", "a",
            "-show_entries", "stream=index",
            "-of", "csv=p=0",
            video_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if not result.stdout.strip():
            return 0
        return len(result.stdout.strip().split("\n"))
    except (subprocess.SubprocessError, FileNotFoundError):
        return 0


def get_video_duration(video_path: str) -> float:
    """Get duration in seconds using ffprobe. Returns 0 on error."""
    try:
        cmd = [
            "ffprobe", "-loglevel", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0 or not result.stdout.strip():
            return 0.0
        return float(result.stdout.strip())
    except (subprocess.SubprocessError, FileNotFoundError, ValueError):
        return 0.0


def cut_segment(
    video_path: str,
    start_sec: float,
    duration_sec: float,
    out_path: str,
    video_format: str,
) -> bool:
    """Cut one segment (video+audio) from video_path to out_path. Returns True on success."""
    try:
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_sec),
            "-i", video_path,
            "-t", str(duration_sec),
            "-c", "copy",
            "-avoid_negative_ts", "1",
            out_path,
        ]
        r = subprocess.run(cmd, capture_output=True, check=False)
        if r.returncode != 0:
            cmd = [
                "ffmpeg", "-y", "-i", video_path,
                "-ss", str(start_sec), "-t", str(duration_sec),
                out_path,
            ]
            subprocess.run(cmd, capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def build_fixed_clips(
    video_paths: list[str],
    output_dir: str,
    video_format: str,
    num_clips: int,
    clip_duration_sec: float,
    progress_callback: None | callable = None,
    stop_check: None | callable = None,
) -> int:
    """
    From one or more videos, produce exactly num_clips clips, each clip_duration_sec long, with audio.
    Clips are taken in order: first video 0..D, D..2D, ... then next video, etc.
    Returns number of clips actually written.
    """
    clips_dir = os.path.join(output_dir, "clips")
    os.makedirs(clips_dir, exist_ok=True)
    written = 0
    total_needed = num_clips
    current_file_idx = 0
    current_start = 0.0

    while written < total_needed and current_file_idx < len(video_paths):
        if stop_check and stop_check():
            break
        path = video_paths[current_file_idx]
        duration = get_video_duration(path)
        if duration <= 0:
            current_file_idx += 1
            current_start = 0.0
            continue

        while current_start + clip_duration_sec <= duration and written < total_needed:
            if stop_check and stop_check():
                break
            out_name = f"clip_{written + 1:03d}.{video_format}"
            out_path = os.path.join(clips_dir, out_name)
            if progress_callback:
                progress_callback(written + 1, total_needed, os.path.basename(path))
            if cut_segment(path, current_start, clip_duration_sec, out_path, video_format):
                written += 1
            current_start += clip_duration_sec

        if current_start >= duration or current_start + clip_duration_sec > duration:
            current_file_idx += 1
            current_start = 0.0

    return written


def export_video_clip(video_path: str, output_dir: str, video_format: str) -> None:
    """Export one video clip per input: same content, output format in output/clips/."""
    clips_dir = os.path.join(output_dir, "clips")
    os.makedirs(clips_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    out_path = os.path.join(clips_dir, f"{base_name}.{video_format}")
    try:
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-c", "copy", "-y", out_path],
            capture_output=True,
            check=True,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        try:
            subprocess.run(
                ["ffmpeg", "-i", video_path, "-y", out_path],
                capture_output=True,
                check=True,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            pass


def extract_audio_tracks(video_path: str, output_dir: str, audio_format: str) -> None:
    """Extract all audio tracks from a video file."""
    count = get_audio_track_count(video_path)
    if count == 0:
        return
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    audio_dir = os.path.join(output_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    codec_map = {"mp3": "libmp3lame", "m4a": "aac", "wav": "pcm_s16le", "ogg": "libvorbis"}
    codec = codec_map.get(audio_format, "copy")

    for i in range(count):
        out_file = os.path.join(audio_dir, f"{base_name}-track-{i}.{audio_format}")
        cmd = [
            "ffmpeg", "-i", video_path,
            "-map", f"0:a:{i}", "-vn",
            "-acodec", codec, "-y", out_file,
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            pass


def _get_ffmpeg_dir() -> str | None:
    """Find directory containing ffmpeg.exe (PATH or WinGet install). Returns None if not found."""
    # 1. Check if ffmpeg is already in PATH
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return ""  # empty = use PATH as-is
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # 2. Windows: check WinGet Links (winget installs often not in PATH for existing processes)
    if sys.platform == "win32":
        localappdata = os.environ.get("LOCALAPPDATA", "")
        winget_links = os.path.join(localappdata, "Microsoft", "WinGet", "Links")
        ffmpeg_exe = os.path.join(winget_links, "ffmpeg.exe")
        if os.path.isfile(ffmpeg_exe):
            return winget_links

        # 3. Scan WinGet Packages for Gyan.FFmpeg
        winget_packages = os.path.join(localappdata, "Microsoft", "WinGet", "Packages")
        if os.path.isdir(winget_packages):
            for name in os.listdir(winget_packages):
                if "Gyan.FFmpeg" in name or "ffmpeg" in name.lower():
                    p = os.path.join(winget_packages, name)
                    if os.path.isdir(p):
                        # Look for bin folder or ffmpeg.exe in root
                        for candidate in [p, os.path.join(p, "bin")]:
                            if os.path.isfile(os.path.join(candidate, "ffmpeg.exe")):
                                return candidate
    return None


def _ensure_ffmpeg_in_path() -> None:
    """If ffmpeg is found in WinGet (or similar) but not in PATH, prepend it for this process."""
    ffmpeg_dir = _get_ffmpeg_dir()
    if ffmpeg_dir is None:
        return
    if ffmpeg_dir and ffmpeg_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available (after ensuring WinGet path is applied)."""
    _ensure_ffmpeg_in_path()
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def get_video_files_from_folder(folder: str) -> list[str]:
    """Return list of video file paths in folder."""
    if not os.path.isdir(folder):
        return []
    paths = []
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if os.path.isfile(path) and os.path.splitext(name)[1].lower() in VIDEO_EXTENSIONS:
            paths.append(path)
    return paths


class VideoEditorApp:
    def __init__(self):
        # Ensure FFmpeg from WinGet is on PATH (fixes "FFmpeg missing" when launched from editor)
        _ensure_ffmpeg_in_path()

        self.root = tk.Tk()
        self.root.title("Video Editor AI - Automatic Video Editor")
        self.root.geometry("800x650")
        self.root.minsize(600, 500)

        self.selected_files: list[str] = []
        self.processing = False
        self.stop_requested = False

        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        # Header
        ttk.Label(main, text="Video Editor AI", font=("", 18)).pack(anchor=tk.W)
        ttk.Label(main, text="Automatic video editing with minimal interaction", font=("", 10)).pack(anchor=tk.W)
        ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # File selection
        file_frame = ttk.LabelFrame(main, text="Video Files", padding=5)
        file_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Select Video Files", command=self._select_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Select Folder", command=self._select_folder).pack(side=tk.LEFT)

        self.file_list = scrolledtext.ScrolledText(file_frame, height=6, state=tk.DISABLED, wrap=tk.WORD)
        self.file_list.pack(fill=tk.BOTH, expand=True, pady=5)
        self.file_count_label = ttk.Label(file_frame, text="Selected: 0 file(s)")
        self.file_count_label.pack(anchor=tk.W)

        # Output settings
        settings_frame = ttk.LabelFrame(main, text="Output Settings", padding=5)
        settings_frame.pack(fill=tk.X, pady=5)

        out_row = ttk.Frame(settings_frame)
        out_row.pack(fill=tk.X)
        ttk.Label(out_row, text="Output directory:", width=14).pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "output"))
        ttk.Entry(out_row, textvariable=self.output_dir_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(out_row, text="Browse", command=self._browse_output).pack(side=tk.LEFT)

        fmt_row = ttk.Frame(settings_frame)
        fmt_row.pack(fill=tk.X, pady=5)
        ttk.Label(fmt_row, text="Video format:", width=14).pack(side=tk.LEFT)
        self.video_fmt_var = tk.StringVar(value="mp4")
        ttk.Combobox(fmt_row, textvariable=self.video_fmt_var, values=VIDEO_FORMATS, width=10, state="readonly").pack(side=tk.LEFT, padx=5)
        ttk.Label(fmt_row, text="Audio format:", width=14).pack(side=tk.LEFT, padx=(20, 0))
        self.audio_fmt_var = tk.StringVar(value="wav")
        ttk.Combobox(fmt_row, textvariable=self.audio_fmt_var, values=AUDIO_FORMATS, width=10, state="readonly").pack(side=tk.LEFT, padx=5)
        self.combine_audio_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Combine all audio tracks into one", variable=self.combine_audio_var).pack(anchor=tk.W)

        # 6-sec clip mode: N clips × 6 sec = 60 or 120 sec total, each with audio
        clip_row = ttk.Frame(settings_frame)
        clip_row.pack(fill=tk.X, pady=5)
        ttk.Label(clip_row, text="Number of clips:", width=14).pack(side=tk.LEFT)
        self.num_clips_var = tk.StringVar(value="20")
        ttk.Combobox(clip_row, textvariable=self.num_clips_var, values=["10", "20"], width=6, state="readonly").pack(side=tk.LEFT, padx=5)
        ttk.Label(clip_row, text="Clip duration (sec):", width=16).pack(side=tk.LEFT, padx=(10, 0))
        self.clip_duration_var = tk.StringVar(value="6")
        ttk.Spinbox(clip_row, textvariable=self.clip_duration_var, from_=1, to=60, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(clip_row, text="(e.g. 20 × 6 sec = 120 sec total)", font=("", 9)).pack(side=tk.LEFT, padx=5)

        # Processing
        proc_frame = ttk.LabelFrame(main, text="Processing", padding=5)
        proc_frame.pack(fill=tk.X, pady=5)

        btn_row = ttk.Frame(proc_frame)
        btn_row.pack(fill=tk.X)
        self.start_btn = ttk.Button(btn_row, text="Start Processing", command=self._start_processing)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.stop_btn = ttk.Button(btn_row, text="Stop", command=self._stop_processing, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress = ttk.Progressbar(proc_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=5)

        self.status_var = tk.StringVar(value="Ready. Select video files and click Start.")
        ttk.Label(proc_frame, textvariable=self.status_var, wraplength=700).pack(anchor=tk.W)

    def _update_file_display(self):
        self.file_list.config(state=tk.NORMAL)
        self.file_list.delete(1.0, tk.END)
        self.file_list.insert(tk.END, "\n".join(self.selected_files) or "No files selected.")
        self.file_list.config(state=tk.DISABLED)
        self.file_count_label.config(text=f"Selected: {len(self.selected_files)} file(s)")

    def _select_files(self):
        paths = filedialog.askopenfilenames(
            title="Select video files",
            filetypes=[("Video files", " ".join(f"*{e}" for e in VIDEO_EXTENSIONS)), ("All files", "*.*")],
        )
        if paths:
            self.selected_files = list(paths)
            self._update_file_display()
            self.status_var.set(f"Selected {len(self.selected_files)} file(s).")

    def _select_folder(self):
        folder = filedialog.askdirectory(title="Select folder with videos")
        if folder:
            files = get_video_files_from_folder(folder)
            if files:
                self.selected_files = files
                self._update_file_display()
                self.status_var.set(f"Found {len(files)} video(s) in folder.")
            else:
                messagebox.showinfo("No videos", "No video files found in the selected folder.")

    def _browse_output(self):
        path = filedialog.askdirectory(title="Select output directory")
        if path:
            self.output_dir_var.set(path)

    def _start_processing(self):
        if not self.selected_files:
            messagebox.showwarning("No files", "Please select video files first.")
            return
        if not check_ffmpeg():
            messagebox.showerror("FFmpeg missing", "FFmpeg is not installed or not in PATH. Please install FFmpeg.")
            return
        self.processing = True
        self.stop_requested = False
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_var.set("Processing...")
        threading.Thread(target=self._process_videos, daemon=True).start()

    def _stop_processing(self):
        self.stop_requested = True
        self.status_var.set("Stopping...")

    def _process_videos(self):
        output_dir = self.output_dir_var.get().strip() or os.path.join(os.getcwd(), "output")
        audio_fmt = self.audio_fmt_var.get()
        video_fmt = self.video_fmt_var.get()
        try:
            num_clips = int(self.num_clips_var.get().strip() or "20")
            num_clips = max(1, min(100, num_clips))
        except ValueError:
            num_clips = 20
        try:
            clip_duration = float(self.clip_duration_var.get().strip() or "6")
            clip_duration = max(0.5, min(120.0, clip_duration))
        except ValueError:
            clip_duration = 6.0

        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "audio"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "clips"), exist_ok=True)

        def on_progress(current: int, total: int, source_name: str) -> None:
            self.root.after(0, lambda: self.status_var.set(f"Clip {current}/{total} from {source_name}"))
            self.root.after(0, lambda: self.progress_var.set(100.0 * current / total if total else 0))

        def should_stop() -> bool:
            return self.stop_requested

        # 1) Build N clips of D sec each (with audio) → output/clips/clip_001.mp4, ...
        written = build_fixed_clips(
            self.selected_files,
            output_dir,
            video_fmt,
            num_clips=num_clips,
            clip_duration_sec=clip_duration,
            progress_callback=on_progress,
            stop_check=should_stop,
        )

        # 2) Extract full audio tracks → output/audio/ (optional, for reference)
        for i, path in enumerate(self.selected_files):
            if self.stop_requested:
                break
            extract_audio_tracks(path, output_dir, audio_fmt)

        self.root.after(0, self.progress_var.set, 100.0)
        self.processing = False
        self.root.after(0, lambda: self._on_processing_done(written, num_clips, clip_duration))

    def _on_processing_done(self):
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        count = len(self.selected_files)
        self.status_var.set(f"Done. Processed {count} file(s). Output in: {self.output_dir_var.get()}")
        out = self.output_dir_var.get()
        messagebox.showinfo(
            "Complete",
            f"Processed {count} file(s).\n\n"
            f"Output: {out}\n"
            f"  • Clips (video): {out}/clips/\n"
            f"  • Audio: {out}/audio/",
        )

    def run(self):
        self.root.mainloop()


def main():
    app = VideoEditorApp()
    app.run()


if __name__ == "__main__":
    main()
