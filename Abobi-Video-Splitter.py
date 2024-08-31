import sys
import os
import subprocess
import random
import json
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

CONFIG_FILE = "last_config.json"  # Changed to reflect single configuration

class Worker(QtCore.QThread):
    update_progress = QtCore.pyqtSignal(str)
    finished_signal = QtCore.pyqtSignal()

    def __init__(self, video_files, split_folder, clip_duration, num_clips):
        super().__init__()
        self.video_files = video_files
        self.split_folder = split_folder
        self.clip_duration = clip_duration
        self.num_clips = num_clips

    def run(self):
        for input_file in self.video_files:
            input_path = Path(input_file)
            os.makedirs(self.split_folder, exist_ok=True)
            self.create_random_clips(input_path, self.split_folder, self.clip_duration, self.num_clips)
            self.update_progress.emit(f"Completed: {input_path.name}")
        self.finished_signal.emit()

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
                    '-c:v', 'libx265',
                    '-crf', '18',
                    '-c:a', 'aac',
                    '-vf', 'scale=-1:-1',
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
        self.output_folder = r"E:\Os simpsons"
        self.split_folder = r"C:\Users\abobi\Videos\Os simpsons edited"
        self.video_files = []
        self.num_to_split = 10
        self.is_processing = False
        self.clip_duration = 59
        self.config = self.load_config()

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

        self.lineEdit_inputFolder = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_inputFolder.setGeometry(QtCore.QRect(10, 70, 280, 38))
        self.lineEdit_inputFolder.setPlaceholderText("Enter input folder path here")
        self.lineEdit_inputFolder.setObjectName("lineEdit_inputFolder")

        self.lineEdit_splitFolder = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_splitFolder.setGeometry(QtCore.QRect(300, 70, 280, 38))
        self.lineEdit_splitFolder.setPlaceholderText("Enter split folder path here")
        self.lineEdit_splitFolder.setObjectName("lineEdit_splitFolder")

        self.lineEdit_clipDuration = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_clipDuration.setGeometry(QtCore.QRect(10, 120, 280, 38))
        self.lineEdit_clipDuration.setPlaceholderText("Clip duration in seconds")
        self.lineEdit_clipDuration.setObjectName("lineEdit_clipDuration")

        self.lineEdit_numFiles = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_numFiles.setGeometry(QtCore.QRect(300, 120, 280, 38))
        self.lineEdit_numFiles.setPlaceholderText("Number of files to split")
        self.lineEdit_numFiles.setObjectName("lineEdit_numFiles")

        self.lineEdit_numClips = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_numClips.setGeometry(QtCore.QRect(10, 170, 280, 38))
        self.lineEdit_numClips.setPlaceholderText("Number of clips per video")
        self.lineEdit_numClips.setObjectName("lineEdit_numClips")

        self.pushButton_process = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_process.setGeometry(QtCore.QRect(300, 270, 280, 38))
        self.pushButton_process.setObjectName("pushButton_process")

        self.textEdit_log = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_log.setGeometry(QtCore.QRect(10, 320, 580, 260))
        self.textEdit_log.setStyleSheet("background-color: #181926; color: #fff;")
        self.textEdit_log.setObjectName("textEdit_log")

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.pushButton_process.clicked.connect(self.process_videos)
        self.log_signal.connect(self.update_log)

        # Load the saved configuration into the interface
        self.load_config_to_interface()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Abobi Spliter"))
        self.label.setText(_translate("MainWindow", "Abobi Spliter"))
        self.pushButton_process.setText(_translate("MainWindow", "Process Videos"))

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

        self.output_folder = self.lineEdit_inputFolder.text().strip()
        self.split_folder = self.lineEdit_splitFolder.text().strip()

        if not self.output_folder:
            self.show_error("Please enter a valid input folder path.")
            return

        if not self.split_folder:
            self.show_error("Please enter a valid split folder path.")
            return

        self.video_files = []
        input_path = Path(self.output_folder)

        if not input_path.exists() or not input_path.is_dir():
            self.show_error("The provided input folder path does not exist or is not a directory.")
            return

        for file_path in input_path.rglob('*'):
            if file_path.suffix.lower() in ['.mp4', '.mkv', '.avi', '.webm', '.mov']:
                self.video_files.append(str(file_path))

        if not self.video_files:
            self.show_error("No video files found in the input folder.")
            return

        try:
            self.clip_duration = int(self.lineEdit_clipDuration.text())
            self.num_to_split = int(self.lineEdit_numFiles.text())
            num_clips = int(self.lineEdit_numClips.text())
        except ValueError:
            self.show_error("Please enter valid numeric values for clip duration, number of files, and number of clips.")
            return

        self.save_config(self.output_folder, self.split_folder, self.clip_duration, self.num_to_split, num_clips)

        self.is_processing = True
        self.log("Starting video processing...")

        self.worker = Worker(self.video_files[:self.num_to_split], self.split_folder, self.clip_duration, num_clips)
        self.worker.update_progress.connect(self.log)
        self.worker.finished_signal.connect(self.on_processing_finished)
        self.worker.start()

    def show_error(self, message):
        QMessageBox.critical(None, "Error", message, QMessageBox.Ok)

    def on_processing_finished(self):
        self.is_processing = False
        self.log("Processing completed.")

    def save_config(self, output_folder, split_folder, clip_duration, num_to_split, num_clips):
        new_config = {
            "output_folder": output_folder,
            "split_folder": split_folder,
            "clip_duration": clip_duration,
            "num_to_split": num_to_split,
            "num_clips": num_clips
        }

        # Save the latest configuration only
        with open(CONFIG_FILE, 'w') as f:
            json.dump(new_config, f, indent=4)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def load_config_to_interface(self):
        config = self.load_config()
        if config:
            self.lineEdit_inputFolder.setText(config.get("output_folder", ""))
            self.lineEdit_splitFolder.setText(config.get("split_folder", ""))
            self.lineEdit_clipDuration.setText(str(config.get("clip_duration", "")))
            self.lineEdit_numFiles.setText(str(config.get("num_to_split", "")))
            self.lineEdit_numClips.setText(str(config.get("num_clips", "")))

def main():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
