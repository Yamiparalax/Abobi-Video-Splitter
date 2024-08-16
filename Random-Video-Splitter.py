import sys
from playsound import playsound
import os
import subprocess
import random
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QMessageBox


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

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 550)
        MainWindow.setStyleSheet("background-color: #24273a; color: #fff;")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(170, 0, 261, 61))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.pushButton_selectFolder = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_selectFolder.setGeometry(QtCore.QRect(10, 70, 150, 38))
        self.pushButton_selectFolder.setObjectName("pushButton_selectFolder")

        self.pushButton_selectSplitFolder = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_selectSplitFolder.setGeometry(QtCore.QRect(170, 70, 150, 38))
        self.pushButton_selectSplitFolder.setObjectName("pushButton_selectSplitFolder")

        self.pushButton_process = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_process.setGeometry(QtCore.QRect(330, 70, 150, 38))
        self.pushButton_process.setObjectName("pushButton_process")

        self.textEdit_log = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_log.setGeometry(QtCore.QRect(10, 120, 580, 400))
        self.textEdit_log.setStyleSheet("background-color: #181926; color: #fff;")
        self.textEdit_log.setObjectName("textEdit_log")

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.pushButton_selectFolder.clicked.connect(self.select_folder)
        self.pushButton_selectSplitFolder.clicked.connect(self.select_split_folder)
        self.pushButton_process.clicked.connect(self.process_videos)

        self.log_signal.connect(self.update_log)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Video Cutter"))
        self.label.setText(_translate("MainWindow", "Video Cutter"))
        self.pushButton_selectFolder.setText(_translate("MainWindow", "Select Input Folder"))
        self.pushButton_selectSplitFolder.setText(_translate("MainWindow", "Select Split Folder"))
        self.pushButton_process.setText(_translate("MainWindow", "Process Videos"))

    @QtCore.pyqtSlot(str)
    def update_log(self, message):
        self.textEdit_log.append(message)
        self.textEdit_log.verticalScrollBar().setValue(self.textEdit_log.verticalScrollBar().maximum())

    def log(self, message):
        self.log_signal.emit(message)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(None, "Select Input Folder")
        if folder:
            self.output_folder = folder
            self.log(f"Selected input folder: {folder}")

            # Clear previous video files
            self.video_files = []

            # Scan for video files in the selected folder
            self.video_files.extend(Path(folder).glob("*.mp4"))
            self.video_files.extend(Path(folder).glob("*.mkv"))
            self.video_files.extend(Path(folder).glob("*.avi"))
            self.video_files.extend(Path(folder).glob("*.webm"))

            # Log the total number of files found
            total_files = len(self.video_files)
            self.log(f"Total video files found: {total_files}")

            if total_files == 0:
                self.log("No video files found in the selected folder.")

    def select_split_folder(self):
        folder = QFileDialog.getExistingDirectory(None, "Select Split Folder")
        if folder:
            self.split_folder = folder
            self.log(f"Selected split folder: {folder}")

    def process_videos(self):
        if self.is_processing:
            self.show_error("Already processing videos.")
            return

        if not self.output_folder or not self.video_files:
            self.show_error("Please select an input folder with video files.")
            return

        if not self.split_folder:
            self.show_error("Please select a folder where the split files will be saved.")
            return

        num_to_split, ok = QInputDialog.getInt(None, "Number of Files",
                                               f"There are {len(self.video_files)} files. How many do you want to split?",
                                               min=1, max=len(self.video_files))
        if not ok or num_to_split < 1:
            self.show_error("Operation canceled or invalid number entered.")
            return

        metadata_value, ok = QInputDialog.getText(None, "Insert Metadata",
                                                  "Enter metadata value (artist, album, and comment):")
        if not ok or not metadata_value:
            self.show_error("Operation canceled or invalid input.")
            return

        self.custom_metadata = {
            "artist": metadata_value,
            "album": metadata_value,
            "comment": f"Created by {metadata_value}",
            "date": "2000-06-27"
        }

        num_clips, ok = QInputDialog.getInt(None, "Number of Clips per Video",
                                            "How many clips do you want to generate per video?",
                                            min=1, max=20)
        if not ok or num_clips < 1:
            self.show_error("Operation canceled or invalid number of clips entered.")
            return

        selected_files = random.sample(self.video_files, num_to_split)
        self.is_processing = True
        self.log("Starting to process videos...")

        self.worker = Worker(selected_files, self.split_folder, self.custom_metadata, self.clip_duration, num_clips)
        self.worker.update_progress.connect(self.log)
        self.worker.finished_signal.connect(self.on_process_finished)
        self.worker.start()

    def show_error(self, message):
        QMessageBox.critical(None, "Error", message)

    def on_process_finished(self):
        self.is_processing = False
        self.log("Video processing completed.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
