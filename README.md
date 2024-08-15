# Random Video Clip Generator

This script allows you to randomly generate 60-second video clips from selected video files. It supports MP4, MKV, AVI, and WEBM formats. The clips are created using the H265 codec for video and AAC for audio. Additionally, custom metadata such as artist, album, and comments are added to each clip.

## Features

- **Random Clip Generation**: Selects random segments from videos and generates 60-second clips.
- **Custom Metadata**: Allows you to input custom metadata (artist, album, comment, and date) that will be embedded in each generated clip.
- **Multiple Formats Supported**: Handles MP4, MKV, AVI, and WEBM video files.
- **GUI Interaction**: Uses PyQt5 for a graphical interface, making it easier to select folders and input metadata.

## Prerequisites

- Python 3.x installed on your system.
- Required Python packages: `moviepy`, `PyQt5`.
- `ffmpeg` installed and accessible via command line.

## Installation

1. Clone the repository or download the script.
2. Install the required Python packages using pip:

   ```bash
   pip install moviepy PyQt5
   ```

3. Ensure `ffmpeg` is installed on your system and accessible from the command line.

## Usage

1. Run the script using Python:

   ```bash
   python script_name.py
   ```

2. **Step 1**: Select the folder containing the video files you want to process.
3. **Step 2**: Specify the number of files to split from the selected folder.
4. **Step 3**: Select an output folder where the generated clips will be saved.
5. **Step 4**: Input custom metadata values (artist, album, and comment) that will be applied to the clips.

## Important Notes

- The videos need to be at least 4 minutes long for the script to generate the clips.
- The script uses a random selection process to generate the clips, ensuring variety in each execution.

## Contact

For any questions or issues, you can reach out to me through the following platforms:

- **Email**: [carlosfrenesi01@gmail.com](mailto:carlosfrenesi01@gmail.com)
- **LinkedIn**: [Carlos Eduardo](https://www.linkedin.com/in/abobicarlo/)
- **Instagram**: [@abobicarlos](https://instagram.com/abobicarlos)