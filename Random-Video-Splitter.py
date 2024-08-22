import sys
import os
import json
import subprocess
import random
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QInputDialog, QMessageBox


class Worker(QtCore.QThread):
    update_progress = QtCore.pyqtSignal(str)  # Signal to update the interface
    finished_signal = QtCore.pyqtSignal()  # Signal to indicate work is finished

    def __init__(self, video_files, split_folder, clip_duration, num_clips):
        super().__init__()
        self.video_files = video_files
        self.split_folder = split_folder
        self.clip_duration = clip_duration
        self.num_clips = num_clips

    def run(self):
        for input_file in self.video_files:
            input_path = Path(input_file)
            # Ensure the split folder exists
            os.makedirs(self.split_folder, exist_ok=True)
            self.create_random_clips(input_path, self.split_folder, self.clip_duration, self.num_clips)
            self.update_progress.emit(f"Completed: {input_path.name}")
        self.finished_signal.emit()  # Emit signal when process is finished

    def create_random_clips(self, input_path, output_folder, clip_duration=59, num_clips=5):
        try:
            video = VideoFileClip(str(input_path))
            total_duration = video.duration

            for i in range(num_clips):
                start = random.uniform(59, total_duration - clip_duration - 59)
                end = start + clip_duration

                random_clip_path = Path(output_folder) / f"{input_path.stem} - {i + 1}.mp4"
                command = [
                    'ffmpeg',
                    '-y',
                    '-ss', f'{start:.2f}',
                    '-i', str(input_path),
                    '-t', f'{clip_duration:.2f}',
                    '-c:v', 'libx265',  # Changed to use H.265 codec
                    '-c:a', 'aac',
                    '-preset', 'ultrafast',
                    '-vf', 'scale=1280:-1',
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
        self.is_processing = False
        self.clip_duration = 59
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

        # Input folder path
        self.lineEdit_inputFolder = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_inputFolder.setGeometry(QtCore.QRect(10, 70, 280, 38))
        self.lineEdit_inputFolder.setPlaceholderText("Enter input folder path here")
        self.lineEdit_inputFolder.setObjectName("lineEdit_inputFolder")

        # Split folder path
        self.lineEdit_splitFolder = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_splitFolder.setGeometry(QtCore.QRect(300, 70, 280, 38))
        self.lineEdit_splitFolder.setPlaceholderText("Enter split folder path here")
        self.lineEdit_splitFolder.setObjectName("lineEdit_splitFolder")

        # Clip duration
        self.lineEdit_clipDuration = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_clipDuration.setGeometry(QtCore.QRect(10, 120, 280, 38))
        self.lineEdit_clipDuration.setPlaceholderText("Clip duration in seconds")
        self.lineEdit_clipDuration.setObjectName("lineEdit_clipDuration")

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

        # Button to load previous settings
        self.pushButton_loadHistory = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_loadHistory.setGeometry(QtCore.QRect(300, 170, 280, 38))
        self.pushButton_loadHistory.setObjectName("pushButton_loadHistory")

        # Process button
        self.pushButton_process = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_process.setGeometry(QtCore.QRect(10, 220, 580, 38))
        self.pushButton_process.setObjectName("pushButton_process")

        # Text area for logs
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
        self.pushButton_loadHistory.setText(_translate("MainWindow", "Load Previous Settings"))

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

        # Get paths from text fields
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

        # Scan for video files in the input folder
        self.video_files.extend(Path(self.output_folder).glob("*.mp4"))
        self.video_files.extend(Path(self.output_folder).glob("*.mkv"))
        self.video_files.extend(Path(self.output_folder).glob("*.avi"))
        self.video_files.extend(Path(self.output_folder).glob("*.webm"))

        # Log total number of files found
        total_files = len(self.video_files)
        self.log(f"Total video files found: {total_files}")

        if total_files == 0:
            self.log("No video files found in the input folder.")
            return

        try:
            num_to_split = int(self.lineEdit_numFiles.text().strip())
            if num_to_split < 1 or num_to_split > total_files:
                raise ValueError("Invalid number of files to split.")
        except ValueError:
            self.show_error("Please enter a valid number of files to split.")
            return

        try:
            clip_duration = int(self.lineEdit_clipDuration.text().strip())
            if clip_duration <= 0:
                raise ValueError("Invalid clip duration.")
        except ValueError:
            self.show_error("Please enter a valid clip duration.")
            return

        try:
            num_clips = int(self.lineEdit_numClips.text().strip())
            if num_clips <= 0:
                raise ValueError("Invalid number of clips per video.")
        except ValueError:
            self.show_error("Please enter a valid number of clips per video.")
            return

        self.save_history()  # Save current settings

        # Randomly select files to split
        selected_files = random.sample(self.video_files, num_to_split)
        self.is_processing = True

        # Start the Worker
        self.worker = Worker(selected_files, self.split_folder, clip_duration, num_clips)
        self.worker.update_progress.connect(self.log)
        self.worker.finished_signal.connect(self.processing_finished)
        self.worker.start()

    def processing_finished(self):
        self.is_processing = False
        self.log("Video processing completed.")

    def show_error(self, message):
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setWindowTitle("Error")
        error_msg.setText(message)
        error_msg.exec_()

    def load_history(self):
        if not Path(self.history_file).exists():
            return

        try:
            with open(self.history_file, 'r') as file:  # Changed to read mode
                history = json.load(file)
                self.lineEdit_inputFolder.setText(history.get("input_folder", ""))
                self.lineEdit_splitFolder.setText(history.get("split_folder", ""))
                self.lineEdit_clipDuration.setText(str(history.get("clip_duration", "59")))
                self.lineEdit_numFiles.setText(str(history.get("num_to_split", "0")))
                self.lineEdit_numClips.setText(str(history.get("num_clips", "5")))
        except Exception as e:
            self.log(f"Error loading history: {e}")

    def save_history(self):
        history = {
            "input_folder": self.output_folder,
            "split_folder": self.split_folder,
            "clip_duration": self.lineEdit_clipDuration.text().strip(),
            "num_to_split": self.lineEdit_numFiles.text().strip(),
            "num_clips": self.lineEdit_numClips.text().strip()
        }

        try:
            with open(self.history_file, 'w') as file:
                json.dump(history, file)
        except Exception as e:
            self.log(f"Error saving history: {e}")

    def load_previous_settings(self):
        self.load_history()


def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
