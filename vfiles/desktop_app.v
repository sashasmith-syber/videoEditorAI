module main

import os
import ui
import videoeditor.desktop.video_processor as vp
import videoeditor.desktop.file_manager as fm

struct AppState {
mut:
	selected_files     []string
	output_dir         string
	video_format       string = 'mp4'
	audio_format       string = 'wav'
	combine_audio      bool
	processing         bool
	status_message     string = 'Ready'
	progress           f32
	working_dir        string
}

fn main() {
	mut app := &AppState{
		working_dir: os.getwd()
		output_dir: os.join_path(os.getwd(), 'output')
	}
	
	window := ui.window(
		width: 900
		height: 700
		title: 'Video Editor AI - Automatic Video Editor'
		mode: .resizable
		state: app
		on_init: window_init
		children: [
			ui.column(
				margin: ui.MarginConfig{10, 10, 10, 10}
				spacing: 15
				children: [
					// Header
					ui.row(
						spacing: 10
						children: [
							ui.label(
								text: 'Video Editor AI'
								size: 24
							),
							ui.label(
								text: 'Automatic video editing with minimal interaction'
								size: 12
							),
						]
					),
					ui.separator(),
					
					// File Selection Section
					ui.group(
						title: 'Video Files'
						margin: ui.MarginConfig{5, 5, 5, 5}
						children: [
							ui.column(
								spacing: 10
								children: [
									ui.row(
										spacing: 10
										children: [
											ui.button(
												text: 'Select Video Files'
												on_click: select_files
											),
											ui.button(
												text: 'Select Folder'
												on_click: select_folder
											),
										]
									),
									ui.textbox(
										width: 800
										height: 100
										mode: .multiline
										is_read_only: true
										text: &app.selected_files.join('\n')
										placeholder: 'No files selected. Click "Select Video Files" or "Select Folder" to add videos.'
									),
									ui.label(
										text: 'Selected: ${app.selected_files.len} file(s)'
										size: 11
									),
								]
							),
						]
					),
					
					// Settings Section
					ui.group(
						title: 'Output Settings'
						margin: ui.MarginConfig{5, 5, 5, 5}
						children: [
							ui.column(
								spacing: 10
								children: [
									ui.row(
										spacing: 10
										children: [
											ui.label(
												text: 'Output Directory:'
												width: 120
											),
											ui.textbox(
												width: 500
												text: &app.output_dir
											),
											ui.button(
												text: 'Browse'
												on_click: select_output_dir
											),
										]
									),
									ui.row(
										spacing: 10
										children: [
											ui.label(
												text: 'Video Format:'
												width: 120
											),
											ui.dropdown(
												width: 150
												selected_index: 0
												items: ['mp4', 'mkv', 'avi', 'mov']
												on_selection_changed: on_video_format_changed
											),
											ui.label(
												text: 'Audio Format:'
												width: 120
											),
											ui.dropdown(
												width: 150
												selected_index: 2
												items: ['mp3', 'm4a', 'wav', 'ogg']
												on_selection_changed: on_audio_format_changed
											),
										]
									),
									ui.checkbox(
										text: 'Combine all audio tracks into one'
										checked: &app.combine_audio
									),
								]
							),
						]
					),
					
					// Processing Section
					ui.group(
						title: 'Processing'
						margin: ui.MarginConfig{5, 5, 5, 5}
						children: [
							ui.column(
								spacing: 10
								children: [
									ui.row(
										spacing: 10
										children: [
											ui.button(
												text: 'Start Processing'
												on_click: start_processing
												enabled: !app.processing && app.selected_files.len > 0
											),
											ui.button(
												text: 'Stop'
												on_click: stop_processing
												enabled: app.processing
											),
										]
									),
									ui.progressbar(
										width: 800
										value: app.progress
										max: 100
									),
									ui.label(
										text: &app.status_message
										size: 12
									),
								]
							),
						]
					),
				]
			),
		]
	)
	
	ui.run(window)
}

fn window_init(w &ui.Window) {
	// Initialize window
}

fn select_files(mut app AppState, button &ui.Button) {
	files := fm.select_video_files()
	if files.len > 0 {
		app.selected_files = files
		app.status_message = 'Selected ${files.len} file(s)'
	} else {
		app.status_message = 'No files selected'
	}
}

fn select_folder(mut app AppState, button &ui.Button) {
	folder := fm.select_folder()
	if folder != '' {
		files := fm.get_video_files_from_folder(folder)
		if files.len > 0 {
			app.selected_files = files
			app.status_message = 'Found ${files.len} video file(s) in folder'
		} else {
			app.status_message = 'No video files found in selected folder'
		}
	}
}

fn select_output_dir(mut app AppState, button &ui.Button) {
	dir := fm.select_directory()
	if dir != '' {
		app.output_dir = dir
		app.status_message = 'Output directory set to: ${dir}'
	}
}

fn on_video_format_changed(mut app AppState, dropdown &ui.Dropdown) {
	formats := ['mp4', 'mkv', 'avi', 'mov']
	if dropdown.selected_index < formats.len {
		app.video_format = formats[dropdown.selected_index]
	}
}

fn on_audio_format_changed(mut app AppState, dropdown &ui.Dropdown) {
	formats := ['mp3', 'm4a', 'wav', 'ogg']
	if dropdown.selected_index < formats.len {
		app.audio_format = formats[dropdown.selected_index]
	}
}

fn start_processing(mut app AppState, button &ui.Button) {
	if app.selected_files.len == 0 {
		app.status_message = 'Please select video files first'
		return
	}
	
	// Check if ffmpeg is available
	if !vp.check_ffmpeg_available() {
		app.status_message = 'Error: ffmpeg not found. Please install ffmpeg first.'
		return
	}
	
	if !vp.check_ffprobe_available() {
		app.status_message = 'Error: ffprobe not found. Please install ffmpeg first.'
		return
	}
	
	app.processing = true
	app.progress = 0.0
	app.status_message = 'Processing started...'
	
	// Process videos in a separate thread/coroutine
	spawn process_videos(mut app)
}

fn stop_processing(mut app AppState, button &ui.Button) {
	app.processing = false
	app.status_message = 'Processing stopped by user'
}

fn process_videos(mut app AppState) {
	total_files := app.selected_files.len
	
	for i, file in app.selected_files {
		if !app.processing {
			break
		}
		
		app.status_message = 'Processing: ${os.base(file)} (${i + 1}/${total_files})'
		app.progress = f32(i) / f32(total_files) * 100.0
		
		// Process video
		vp.process_video(
			file: file
			output_dir: app.output_dir
			video_format: app.video_format
			audio_format: app.audio_format
			combine_audio: app.combine_audio
		)
	}
	
	app.progress = 100.0
	app.processing = false
	app.status_message = 'Processing completed! Processed ${total_files} file(s)'
}
