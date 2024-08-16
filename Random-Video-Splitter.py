import sys
import os
import subprocess
import threading
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox, QMainWindow, QPushButton, QLabel, QLineEdit, QTextEdit, QVBoxLayout, QWidget
from PyQt5 import QtCore

class VideoSplitter(QtCore.QObject):
    log_signal = QtCore.pyqtSignal(str)
    progress_signal = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def log(self, message):
        self.log_signal.emit(message)

    def set_progress(self, value):
        self.progress_signal.emit(value)

    def create_random_clips(self, input_path, output_folder, custom_metadata, clip_duration=60, num_clips=5):
        try:
            output_folder = Path(output_folder)
            output_folder.mkdir(exist_ok=True)

            video = VideoFileClip(str(input_path))
            total_duration = video.duration

            for i in range(num_clips):
                start = random.uniform(120, total_duration - clip_duration - 120)
                end = start + clip_duration

                random_clip_path = output_folder / f"{input_path.stem} - {i+1}.mp4"
                command = [
                    'ffmpeg',
                    '-y',
                    '-ss', f'{start:.2f}',
                    '-i', str(input_path),
                    '-t', f'{clip_duration:.2f}',
                    '-c:v', 'libx265',
                    '-c:a', 'aac',
                    '-metadata', f'artist={custom_metadata["artist"]}',
                    '-metadata', f'album={custom_metadata["album"]}',
                    '-metadata', f'comment={custom_metadata["comment"]}',
                    '-metadata', f'date={custom_metadata["date"]}',
                    '-strict', 'experimental',
                    '-movflags', '+faststart',
                    '-pix_fmt', 'yuv420p',
                    str(random_clip_path)
                ]
                subprocess.run(command, check=True)

                # Update progress
                self.set_progress((i + 1) / num_clips * 100)

            video.close()
            self.log(f"Random {clip_duration}-second clips created and saved in folder {output_folder}.")

        except Exception as e:
            self.log(f"Error creating random clips for {input_path}: {e}")

    def process_videos(self, video_files, output_folder, num_clips, custom_metadata, num_to_split):
        try:
            selected_files = random.sample(video_files, num_to_split)
            total_files = len(selected_files)

            for idx, input_file in enumerate(selected_files):
                input_path = Path(input_file)

                try:
                    duration = self.get_video_duration(input_path)

                    if duration < 240:  # The video needs to be at least 4 minutes long (240 seconds)
                        self.log(f"The video {input_path} is too short and cannot be split as requested.")
                    else:
                        self.create_random_clips(input_path, output_folder, custom_metadata, 60, num_clips)

                except Exception as e:
                    self.log(f"Error processing video {input_path}: {e}")

                # Update progress
                self.set_progress((idx + 1) / total_files * 100)

            self.log("Splitting completed successfully.")

        except Exception as e:
            self.log(f"Error during video processing: {e}")

    def get_video_duration(self, input_path):
        with VideoFileClip(str(input_path)) as clip:
            return clip.duration

def move_files_to_splits_folder(folder):
    splits_folder = Path(folder) / "splits"
    if not splits_folder.exists():
        splits_folder.mkdir()
    for file in Path(folder).glob("*.*"):
        if file.name != "splits":  # Ensure we don't move the splits folder itself
            file.rename(splits_folder / file.name)
    return splits_folder

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.splitter = VideoSplitter()
        self.thread = None

    def initUI(self):
        self.setWindowTitle('Video Splitter')
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        self.label = QLabel("Video Splitter", self)
        layout.addWidget(self.label)

        self.lineEdit_folder = QLineEdit(self)
        self.lineEdit_folder.setPlaceholderText("Select Folder")
        layout.addWidget(self.lineEdit_folder)

        self.button_select_folder = QPushButton("Select Folder", self)
        self.button_select_folder.clicked.connect(self.select_folder)
        layout.addWidget(self.button_select_folder)

        self.button_start = QPushButton("Start Splitting", self)
        self.button_start.clicked.connect(self.start_splitting)
        layout.addWidget(self.button_start)

        self.textEdit_log = QTextEdit(self)
        self.textEdit_log.setReadOnly(True)
        layout.addWidget(self.textEdit_log)

        self.progress_label = QLabel("Progress: 0%", self)
        layout.addWidget(self.progress_label)

        self.central_widget.setLayout(layout)

        self.splitter.log_signal.connect(self.update_log)
        self.splitter.progress_signal.connect(self.update_progress)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.lineEdit_folder.setText(folder)

    def start_splitting(self):
        folder = self.lineEdit_folder.text()
        if not folder:
            self.show_error("Folder cannot be empty!")
            return

        # Move files to 'splits' folder
        splits_folder = move_files_to_splits_folder(folder)

        num_files, ok = QInputDialog.getInt(self, "Number of Files", "How many files to split?", min=1)
        if not ok or num_files < 1:
            self.show_error("Invalid number of files.")
            return

        num_clips, ok = QInputDialog.getInt(self, "Number of Clips per Video", "How many clips per video?", min=1)
        if not ok or num_clips < 1:
            self.show_error("Invalid number of clips.")
            return

        metadata_value, ok = QInputDialog.getText(self, "Insert Metadata", "Enter metadata value (artist, album, comment):")
        if not ok or not metadata_value:
            self.show_error("Invalid metadata input.")
            return

        custom_metadata = {
            "artist": metadata_value,
            "album": metadata_value,
            "comment": f"Created by {metadata_value}",
            "date": "2000-06-27"
        }

        video_files = list(Path(splits_folder).glob("*.*"))

        if not video_files:
            self.show_error("No video files found in the selected folder.")
            return

        # Start processing in a separate thread
        self.thread = threading.Thread(target=self.splitter.process_videos, args=(video_files, splits_folder, num_clips, custom_metadata, num_files))
        self.thread.start()

    def update_log(self, message):
        self.textEdit_log.append(message)

    def update_progress(self, value):
        self.progress_label.setText(f"Progress: {value:.2f}%")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
