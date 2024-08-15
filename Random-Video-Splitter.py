import sys
import os
import subprocess
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox
import random

def select_folder():
    folder_dialog = QFileDialog()
    folder_dialog.setFileMode(QFileDialog.DirectoryOnly)
    
    if folder_dialog.exec_():
        return folder_dialog.selectedFiles()[0]
    return None

def create_random_clips(input_path, output_folder, clip_duration=60, num_clips=5):
    try:
        output_folder = Path(output_folder)
        output_folder.mkdir(exist_ok=True)

        video = VideoFileClip(str(input_path))
        total_duration = video.duration

        custom_metadata = {
            "artist": "abobisimpsons",
            "album": "abobisimpsons",
            "comment": "Create by abobisimpsons",
            "date": "2000-06-27"
        }

        for i in range(num_clips):
            start = random.uniform(120, total_duration - clip_duration - 120)
            end = start + clip_duration

            random_clip_path = output_folder / f"{input_path.stem} - {i+1}{input_path.suffix}"
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

        video.close()
        print(f"Random 60-second clips created and saved in folder {output_folder}.")

    except Exception as e:
        print(f"Error creating random clips for {input_path}: {e}")

def main():
    app = QApplication(sys.argv)
    
    # Step 1: Select the folder containing the videos
    input_folder = select_folder()
    if not input_folder:
        print("No folder selected.")
        return
    
    input_folder_path = Path(input_folder)
    video_files = list(input_folder_path.glob("*.mp4")) + list(input_folder_path.glob("*.mkv")) + \
                  list(input_folder_path.glob("*.avi")) + list(input_folder_path.glob("*.webm"))
    
    if not video_files:
        print("No video files found in the selected folder.")
        return
    
    # Step 2: Show the number of files in the folder and prompt the user for the number of files to split
    num_files = len(video_files)
    print(f"There are {num_files} files in the folder.")
    
    num_to_split, ok = QInputDialog.getInt(None, "Number of Files", 
                                           f"There are {num_files} files. How many do you want to split?",
                                           min=1, max=num_files)
    
    if not ok or num_to_split < 1:
        print("Operation canceled or invalid number entered.")
        return

    output_folder = select_folder()
    if not output_folder:
        print("No output folder selected.")
        return

    # Step 3: Randomly select files and split them
    selected_files = random.sample(video_files, num_to_split)
    
    for input_file in selected_files:
        input_path = Path(input_file)
        
        try:
            duration = get_video_duration(input_path)
            
            if duration < 240:  # The video needs to be at least 4 minutes long (240 seconds)
                print(f"The video {input_path} is too short and cannot be split as requested.")
            else:
                create_random_clips(input_path, output_folder, 60, 5)
        
        except Exception as e:
            print(f"Error processing video {input_path}: {e}")
    
    # Hold the QApplication event loop open until the user closes it
    QMessageBox.information(None, "Process Completed", "Splitting completed successfully.")
    sys.exit(app.exec_())

def get_video_duration(input_path):
    with VideoFileClip(str(input_path)) as clip:
        return clip.duration

if __name__ == "__main__":
    main()
