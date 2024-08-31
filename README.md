# Abobi Spliter

**Abobi Spliter** is a Python script designed for splitting video files into random clips. It provides a graphical user interface built with PyQt5, allowing users to specify input and output folders, clip duration, and the number of clips to be created per video. The script utilizes `ffmpeg` for video processing and supports various video formats.

## Features

- **Random Clip Generation**: Splits videos into random clips of specified duration.
- **Flexible Configuration**: Allows users to set input/output folders, clip duration, number of files to process, and number of clips per video.
- **Graphical User Interface**: Built with PyQt5 for ease of use.
- **Progress Updates**: Displays real-time progress and completion messages.

## Requirements

- Python 3.x
- PyQt5
- moviepy
- ffmpeg (must be installed separately)

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Yamiparalax/Abobi-Video-Splitter.git
   ```

2. **Navigate to the Directory**:

   ```bash
   cd Abobi-Video-Splitter
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure ffmpeg is Installed**:
   - Download and install `ffmpeg` from [ffmpeg.org](https://ffmpeg.org/download.html).

## Usage

1. **Run the Script**:

   ```bash
   python abobi_spliter.py
   ```

2. **Configure the UI**:
   - **Input Folder Path**: Specify the folder containing the video files.
   - **Split Folder Path**: Specify the folder where the clips will be saved.
   - **Clip Duration**: Enter the duration of each clip in seconds.
   - **Number of Files to Split**: Enter the number of video files to process.
   - **Number of Clips per Video**: Enter the number of clips to generate per video.

3. **Start Processing**:
   - Click the "Process Videos" button to start the splitting process.

4. **Monitor Progress**:
   - The progress and completion status will be displayed in the log area.

## Configuration

The script saves and loads configuration settings using a JSON file (`last_config.json`). This includes the input folder path, split folder path, clip duration, number of files to split, and number of clips per video.

## Troubleshooting

- **Error Creating Clips**: Ensure that `ffmpeg` is correctly installed and accessible from the command line.
- **Invalid Paths**: Verify that the specified folders exist and are accessible.
- **Invalid Numeric Values**: Ensure that numeric fields are correctly entered and within valid ranges.

## Contact

For questions or support, you can reach out via:

- **Email**: [abobicarlo@gmail.com](mailto:abobicarlo@gmail.com)
- **LinkedIn**: [linkedin.com/in/abobicarlo](https://www.linkedin.com/in/abobicarlo/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.