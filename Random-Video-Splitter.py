import sys

# Replace with the actual path to your playsound directory
sys.path.append(r'G:\Meu Drive\felquinhas.py\Random-Video-Splitter\lib\site-packages\playsound-1.3.0')

import playsound
import os
import subprocess
import random
import json
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QInputDialog, QMessageBox


class Worker(QtCore.QThread):
    update_progress = QtCore.pyqtSignal(str)  # Signal to update the UI
    finished_signal = QtCore.pyqtSignal()  # Signal to indicate work is finished

    def __init__(self, video_files, split_folder, custom_metadata, clip_duration, num_clips):
        super().__init__()
        self.video_files = video_files
        self.split_folder = split_folder
        self.custom_metadata = custom_metadata
        self.clip_duration = clip_duration
        self.num_clips = num_clips

    def run(self):
        # Ensure the 'splits' folder exists inside the selected split folder
        splits_folder_path = Path(self.split_folder) / 'splits'
        splits_folder_path.mkdir(parents=True, exist_ok=True)

        for input_file in self.video_files:
            input_path = Path(input_file)
            self.create_random_clips(input_path, splits_folder_path, self.custom_metadata, self.clip_duration, self.num_clips)
            self.update_progress.emit(f"Completed: {input_file.name}")
        self.finished_signal.emit()  # Emit signal when the process finishes

    def create_random_clips(self, input_path, output_folder, custom_metadata, clip_duration=120, num_clips=5):
        try:
            video = VideoFileClip(str(input_path))
            total_duration = video.duration

            for i in range(num_clips):
                start = random.uniform(120, total_duration - clip_duration - 120)
                end = start + clip_duration

                random_clip_path = output_folder / f"{input_path.stem} - {i + 1}.mp4"
                command = [
                    'ffmpeg',
                    '-y',
                    '-ss', f'{start:.2f}',
                    '-i', str(input_path),
                    '-t', f'{clip_duration:.2f}',
                    '-c:v', 'libx265',
                    '-c:a', 'aac',
                    '-preset', 'ultrafast',
                    '-vf', 'scale=1280:-1',
                    '-metadata', f'artist={custom_metadata["artist"]}',
                    '-metadata', f'album={custom_metadata["album"]}',
                    '-metadata', f'comment={custom_metadata["comment"]}',
                    '-metadata', f'date={custom_metadata["date"]}',
                    '-strict', 'experimental',
                    '-movflags', '+faststart',
                    '-pix_fmt', 'yuv420p',
                    str(random_clip_path)
                ]
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode != 0:
                    error_message = result.stderr.decode()
                    self.update_progress.emit(f"Error creating random clips for {input_path}: {error_message}")

            video.close()
        except Exception as e:
            self.update_progress.emit(f"Unexpected error: {e}")


class Ui_MainWindow(QtCore.QObject):
    log_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.output_folder = None
        self.split_folder = None
        self.video_files = []
        self.num_to_split = 0
        self.custom_metadata = {}
        self.is_processing = False
        self.clip_duration = 120
        self.history_file = 'history.json'
        self.load_history()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 600)
        MainWindow.setStyleSheet("background-color: #24273a; color: #fff;")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(170, 0, 261, 61))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setObjectName("label")

        # Input folder path field
        self.lineEdit_inputFolder = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_inputFolder.setGeometry(QtCore.QRect(10, 70, 280, 38))
        self.lineEdit_inputFolder.setPlaceholderText("Enter input folder path here")
        self.lineEdit_inputFolder.setObjectName("lineEdit_inputFolder")

        # Split folder path field
        self.lineEdit_splitFolder = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_splitFolder.setGeometry(QtCore.QRect(300, 70, 280, 38))
        self.lineEdit_splitFolder.setPlaceholderText("Enter split folder path here")
        self.lineEdit_splitFolder.setObjectName("lineEdit_splitFolder")

        # Metadata input
        self.lineEdit_metadata = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_metadata.setGeometry(QtCore.QRect(10, 120, 280, 38))
        self.lineEdit_metadata.setPlaceholderText("Enter metadata (artist, album, comment)")
        self.lineEdit_metadata.setObjectName("lineEdit_metadata")

        # Number of files to split
        self.lineEdit_numFiles = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_numFiles.setGeometry(QtCore.QRect(300, 120, 280, 38))
        self.lineEdit_numFiles.setPlaceholderText("Number of files to split")
        self.lineEdit_numFiles.setObjectName("lineEdit_numFiles")

        # Number of clips per video
        self.lineEdit_numClips = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_numClips.setGeometry(QtCore.QRect(10, 170, 280, 38))
        self.lineEdit_numClips.setPlaceholderText("Number of clips per video")
        self.lineEdit_numClips.setObjectName("lineEdit_numClips")

        # Load previous settings button
        self.pushButton_loadHistory = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_loadHistory.setGeometry(QtCore.QRect(300, 170, 280, 38))
        self.pushButton_loadHistory.setObjectName("pushButton_loadHistory")

        # Process button
        self.pushButton_process = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_process.setGeometry(QtCore.QRect(10, 220, 580, 38))
        self.pushButton_process.setObjectName("pushButton_process")

        # Log text area
        self.textEdit_log = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_log.setGeometry(QtCore.QRect(10, 270, 580, 300))
        self.textEdit_log.setStyleSheet("background-color: #181926; color: #fff;")
        self.textEdit_log.setObjectName("textEdit_log")

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.pushButton_process.clicked.connect(self.process_videos)
        self.pushButton_loadHistory.clicked.connect(self.load_previous_settings)

        self.log_signal.connect(self.update_log)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Video Cutter"))
        self.label.setText(_translate("MainWindow", "Video Cutter"))
        self.pushButton_process.setText(_translate("MainWindow", "Process Videos"))
        self.pushButton_loadHistory.setText(_translate("MainWindow", "Use Previous Settings"))

    @QtCore.pyqtSlot(str)
    def update_log(self, message):
        self.textEdit_log.append(message)
        self.textEdit_log.verticalScrollBar().setValue(self.textEdit_log.verticalScrollBar().maximum())

    def log(self, message):
        self.log_signal.emit(message)

    def process_videos(self):
        if self.is_processing:
            self.show_error("Already processing videos.")
            return

        # Get folder paths from the text fields
        self.output_folder = self.lineEdit_inputFolder.text().strip()
        self.split_folder = self.lineEdit_splitFolder.text().strip()

        if not self.output_folder:
            self.show_error("Please enter a valid input folder path.")
            return

        if not self.split_folder:
            self.show_error("Please enter a valid split folder path.")
            return

        # Clear previous video files
        self.video_files = []

        # Scan for video files in the entered input folder
        self.video_files.extend(Path(self.output_folder).glob("*.mp4"))
        self.video_files.extend(Path(self.output_folder).glob("*.mkv"))
        self.video_files.extend(Path(self.output_folder).glob("*.avi"))
        self.video_files.extend(Path(self.output_folder).glob("*.webm"))

        # Log the total number of files found
        total_files = len(self.video_files)
        self.log(f"Total video files found: {total_files}")

        if total_files == 0:
            self.log("No video files found in the entered input folder.")
            return

        try:
            num_to_split = int(self.lineEdit_numFiles.text().strip())
            if num_to_split < 1 or num_to_split > total_files:
                raise ValueError("Invalid number of files to split.")
        except ValueError:
            self.show_error("Invalid number of files to split.")
            return

        try:
            num_clips = int(self.lineEdit_numClips.text().strip())
            if num_clips < 1:
                raise ValueError("Invalid number of clips.")
        except ValueError:
            self.show_error("Invalid number of clips.")
            return

        metadata_value = self.lineEdit_metadata.text().strip()
        if not metadata_value:
            self.show_error("Metadata cannot be empty.")
            return

        self.custom_metadata = {
            "artist": metadata_value,
            "album": metadata_value,
            "comment": f"Created by {metadata_value}",
            "date": "2000-06-27"
        }

        selected_files = random.sample(self.video_files, num_to_split)
        self.is_processing = True
        self.log("Starting to process videos...")

        self.worker = Worker(selected_files, self.split_folder, self.custom_metadata, self.clip_duration, num_clips)
        self.worker.update_progress.connect(self.log)
        self.worker.finished_signal.connect(self.on_process_finished)
        self.worker.start()

        # Save current settings to history
        self.save_history()

    def show_error(self, message):
        QMessageBox.critical(None, "Error", message)

    def on_process_finished(self):
        self.is_processing = False
        self.log("Video processing completed.")

    def save_history(self):
        history = {
            'input_folder': self.output_folder,
            'split_folder': self.split_folder,
            'metadata': self.lineEdit_metadata.text().strip(),
            'num_files': self.lineEdit_numFiles.text().strip(),
            'num_clips': self.lineEdit_numClips.text().strip()
        }
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                all_history = json.load(f)
        else:
            all_history = {'input_folders': [], 'split_folders': [], 'metadata': [], 'num_files': [], 'num_clips': []}

        # Insert new settings at the beginning
        all_history['input_folders'].insert(0, self.output_folder)
        all_history['split_folders'].insert(0, self.split_folder)
        all_history['metadata'].insert(0, history['metadata'])
        all_history['num_files'].insert(0, history['num_files'])
        all_history['num_clips'].insert(0, history['num_clips'])

        # Limit to last 3 entries
        all_history['input_folders'] = all_history['input_folders'][:3]
        all_history['split_folders'] = all_history['split_folders'][:3]
        all_history['metadata'] = all_history['metadata'][:3]
        all_history['num_files'] = all_history['num_files'][:3]
        all_history['num_clips'] = all_history['num_clips'][:3]

        with open(self.history_file, 'w') as f:
            json.dump(all_history, f, indent=4)

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                all_history = json.load(f)
                self.history = all_history
        else:
            self.history = {'input_folders': [], 'split_folders': [], 'metadata': [], 'num_files': [], 'num_clips': []}

    def load_previous_settings(self):
        history = self.history
        if history['input_folders']:
            self.lineEdit_inputFolder.setText(history['input_folders'][0])
        if history['split_folders']:
            self.lineEdit_splitFolder.setText(history['split_folders'][0])
        if history['metadata']:
            self.lineEdit_metadata.setText(history['metadata'][0])
        if history['num_files']:
            self.lineEdit_numFiles.setText(history['num_files'][0])
        if history['num_clips']:
            self.lineEdit_numClips.setText(history['num_clips'][0])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
