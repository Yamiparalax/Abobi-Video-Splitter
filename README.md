# Abobi Cutter

Abobi Cutter is a Python application for processing video files. It allows you to split videos into random clips of a specified duration and save them to a designated folder. This application uses PyQt5 for the graphical user interface and MoviePy for video processing.

## Features

- **Input Folder:** Specify the folder containing video files to be processed.
- **Split Folder:** Define where the processed clips will be saved.
- **Clip Duration:** Set the duration of each clip in seconds.
- **Number of Files:** Choose how many video files to process from the input folder.
- **Number of Clips:** Set how many clips to generate per video.
- **Configuration Saving:** The application saves the last used configuration for easy reuse.

## Requirements

- Python 3.x
- PyQt5
- MoviePy
- FFmpeg (must be installed and available in system PATH)

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/abobi-cutter.git
    cd abobi-cutter
    ```

2. **Install Dependencies:**

    ```bash
    pip install PyQt5 moviepy
    ```

3. **Install FFmpeg:**

    Follow the installation instructions from the [FFmpeg website](https://ffmpeg.org/download.html).

## Usage

1. **Run the Application:**

    ```bash
    python main.py
    ```

2. **Configure the Settings:**
   - **Input Folder:** Enter the path to the folder containing the video files you want to process.
   - **Split Folder:** Enter the path to the folder where the processed clips will be saved.
   - **Clip Duration:** Specify the duration of each clip in seconds.
   - **Number of Files:** Enter the number of video files to process from the input folder.
   - **Number of Clips:** Enter the number of clips to generate per video.

3. **Start Processing:**
   - Click the "Process Videos" button to start processing. The application will save the last configuration used, which will be loaded the next time the application is run.

## Configuration File

The application saves the last used configuration to a file named `last_config.json` in the same directory as the script. This file contains the following settings:

- `output_folder`: The path to the input folder.
- `split_folder`: The path to the output folder.
- `clip_duration`: The duration of each clip in seconds.
- `num_to_split`: The number of video files to process.
- `num_clips`: The number of clips to generate per video.

## Troubleshooting

- **Error Messages:** If you encounter any issues, check the log messages in the interface for details.
- **Invalid Paths:** Ensure that the input and split folder paths are correct and that the folders exist.

## Contributing

Feel free to open issues or submit pull requests if you have suggestions or improvements. Contributions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, please contact [carlosfrenesi01@gmail.com](mailto:your.email@example.com).

 to customize this README with additional information or instructions specific to your needs.