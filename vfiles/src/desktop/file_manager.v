module videoeditor.desktop.file_manager

import os
import os.exec

// Select video files using native file dialog
// Note: This is a simplified version. For full native dialogs, you'd need
// platform-specific bindings or a library like rfd (Rust File Dialog) via V bindings
pub fn select_video_files() []string {
	// For Windows, we can use PowerShell to show file dialog
	$if windows {
		return select_files_windows()
	}
	
	// For Linux, try zenity or kdialog
	$if linux {
		return select_files_linux()
	}
	
	// For macOS, use osascript
	$if macos {
		return select_files_macos()
	}
	
	// Fallback: return empty (user can manually enter paths)
	return []
}

// Windows file selection using PowerShell
fn select_files_windows() []string {
	// PowerShell script to show file dialog
	result := exec.execute('powershell -Command "$dialog = Add-Type -AssemblyName System.Windows.Forms; $ofd = New-Object System.Windows.Forms.OpenFileDialog; $ofd.Filter = \'Video Files|*.mp4;*.mkv;*.avi;*.mov;*.wmv;*.flv;*.webm;*.m4v|All Files|*.*\'; $ofd.Multiselect = $true; if ($ofd.ShowDialog() -eq \'OK\') { $ofd.FileNames -join \'|\' }"') or {
		return []
	}
	
	if result.output.trim_space() == '' {
		return []
	}
	
	return result.output.trim_space().split('|')
}

// Linux file selection using zenity
fn select_files_linux() []string {
	cmd := 'zenity --file-selection --multiple --file-filter="Video files | *.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v" 2>/dev/null'
	result := exec.execute(cmd) or { return [] }
	
	if result.output.trim_space() == '' {
		return []
	}
	
	// zenity returns paths separated by |
	return result.output.trim_space().split('|')
}

// macOS file selection using osascript
fn select_files_macos() []string {
	applescript := '
		tell application "System Events"
			set fileList to choose file with prompt "Select video files" of type {"public.movie"} with multiple selections allowed
			set filePaths to {}
			repeat with aFile in fileList
				set end of filePaths to POSIX path of aFile
			end repeat
			return filePaths as string
		end tell
	'
	
	result := exec.execute('osascript -e "${applescript}"') or { return [] }
	
	if result.output.trim_space() == '' {
		return []
	}
	
	return result.output.trim_space().split(', ')
}

// Select a folder using native folder dialog
pub fn select_folder() string {
	$if windows {
		return select_folder_windows()
	}
	
	$if linux {
		return select_folder_linux()
	}
	
	$if macos {
		return select_folder_macos()
	}
	
	return ''
}

fn select_folder_windows() string {
	result := exec.execute('powershell -Command "$dialog = New-Object System.Windows.Forms.FolderBrowserDialog; if ($dialog.ShowDialog() -eq \'OK\') { $dialog.SelectedPath }"') or {
		return ''
	}
	return result.output.trim_space()
}

fn select_folder_linux() string {
	result := exec.execute('zenity --file-selection --directory 2>/dev/null') or { return '' }
	return result.output.trim_space()
}

fn select_folder_macos() string {
	applescript := 'tell application "System Events" to return POSIX path of (choose folder with prompt "Select folder")'
	result := exec.execute('osascript -e "${applescript}"') or { return '' }
	return result.output.trim_space()
}

// Select output directory
pub fn select_directory() string {
	return select_folder()
}

// Get all video files from a folder
pub fn get_video_files_from_folder(folder_path string) []string {
	mut video_files := []string{}
	
	if !os.exists(folder_path) {
		return video_files
	}
	
	video_extensions := ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v']
	
	files := os.ls(folder_path) or { return video_files }
	
	for file in files {
		file_path := os.join_path(folder_path, file)
		if os.is_file(file_path) {
			ext := os.file_ext(file_path).to_lower()
			if ext in video_extensions {
				video_files << file_path
			}
		}
	}
	
	return video_files
}

// Check if file is a video file
pub fn is_video_file(file_path string) bool {
	video_extensions := ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v']
	ext := os.file_ext(file_path).to_lower()
	return ext in video_extensions
}
