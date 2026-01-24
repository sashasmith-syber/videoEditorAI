module videoeditor.desktop.video_processor

import os
import os.exec

pub struct ProcessConfig {
	file         string
	output_dir   string
	video_format string
	audio_format string
	combine_audio bool
}

// Process a single video file
pub fn process_video(config ProcessConfig) {
	// Ensure output directories exist
	audio_dir := os.join_path(config.output_dir, 'audio')
	clips_dir := os.join_path(config.output_dir, 'clips')
	
	os.mkdir_all(config.output_dir) or { return }
	os.mkdir_all(audio_dir) or { return }
	os.mkdir_all(clips_dir) or { return }
	
	// Extract audio tracks
	extract_audio_tracks(config.file, audio_dir, config.audio_format)
	
	// If combine_audio is requested, combine all extracted tracks
	if config.combine_audio {
		base_name := os.file_name(config.file).replace(os.file_ext(config.file), '')
		audio_files := get_extracted_audio_files(audio_dir, base_name, config.audio_format)
		
		if audio_files.len > 1 {
			combined_output := os.join_path(audio_dir, '${base_name}-combined.${config.audio_format}')
			combine_audio_tracks(audio_files, combined_output)
		}
	}
	
	// Additional processing can be added here:
	// - Cut by silence (future feature)
	// - Export final video with processed audio
}

// Get list of extracted audio files for a video
fn get_extracted_audio_files(audio_dir string, base_name string, audio_format string) []string {
	mut audio_files := []string{}
	
	files := os.ls(audio_dir) or { return audio_files }
	
	for file in files {
		if file.starts_with(base_name) && file.ends_with('.${audio_format}') && !file.contains('combined') {
			audio_files << os.join_path(audio_dir, file)
		}
	}
	
	return audio_files
}

// Extract all audio tracks from a video file
fn extract_audio_tracks(video_path string, output_dir string, audio_format string) {
	// Get number of audio tracks using ffprobe
	audio_track_count := get_audio_track_count(video_path)
	
	if audio_track_count == 0 {
		return
	}
	
	base_name := os.file_name(video_path).replace(os.file_ext(video_path), '')
	
	for i in 0 .. audio_track_count {
		output_file := os.join_path(output_dir, '${base_name}-track-${i}.${audio_format}')
		
		// Extract audio track using ffmpeg
		extract_audio_track(video_path, i, output_file, audio_format)
	}
}

// Get the number of audio tracks in a video
fn get_audio_track_count(video_path string) int {
	// Use ffprobe to count audio tracks
	cmd := 'ffprobe -loglevel error -select_streams a -show_entries stream=index -of csv=p=0 "${video_path}"'
	
	result := exec.execute(cmd) or { return 0 }
	
	// Count lines in output (each line is an audio track index)
	if result.output.trim_space() == '' {
		return 0
	}
	
	tracks := result.output.trim_space().split('\n')
	return tracks.len
}

// Extract a specific audio track from a video
fn extract_audio_track(video_path string, track_index int, output_path string, audio_format string) {
	// Build ffmpeg command to extract audio track
	// -i: input file
	// -map 0:a:${track_index}: map audio track at index
	// -y: overwrite output file
	// -vn: disable video
	// -acodec: audio codec based on format
	mut codec := 'copy' // Default: copy without re-encoding
	
	match audio_format {
		'mp3' { codec = 'libmp3lame' }
		'm4a' { codec = 'aac' }
		'wav' { codec = 'pcm_s16le' }
		'ogg' { codec = 'libvorbis' }
		else { codec = 'copy' }
	}
	
	cmd := 'ffmpeg -i "${video_path}" -map 0:a:${track_index} -vn -acodec ${codec} -y "${output_path}"'
	
	// Execute ffmpeg command (suppress output for cleaner UI)
	result := exec.execute(cmd) or {
		// Error handling - could be logged or shown in UI
		return
	}
	
	// Check if extraction was successful
	if result.exit_code != 0 {
		// Handle error
		return
	}
}

// Cut video by silence (placeholder for future implementation)
pub fn cut_by_silence(video_path string, output_dir string) {
	// This would use ffmpeg's silencedetect filter
	// Implementation would:
	// 1. Detect silence periods
	// 2. Create segments between silence
	// 3. Export individual clips
	
	// Placeholder
}

// Combine multiple audio tracks into one
pub fn combine_audio_tracks(audio_files []string, output_path string) {
	if audio_files.len == 0 {
		return
	}
	
	if audio_files.len == 1 {
		// Just copy the single file
		os.cp(audio_files[0], output_path) or { return }
		return
	}
	
	// Build ffmpeg command to combine audio tracks
	mut cmd := 'ffmpeg'
	
	for file in audio_files {
		cmd += ' -i "${file}"'
	}
	
	// Use filter_complex to mix all audio tracks
	cmd += ' -filter_complex amix=inputs=${audio_files.len}:duration=longest "${output_path}" -y'
	
	exec.execute(cmd) or {
		return
	}
}

// Check if ffmpeg is available
pub fn check_ffmpeg_available() bool {
	result := exec.execute('ffmpeg -version') or { return false }
	return result.exit_code == 0
}

// Check if ffprobe is available
pub fn check_ffprobe_available() bool {
	result := exec.execute('ffprobe -version') or { return false }
	return result.exit_code == 0
}
