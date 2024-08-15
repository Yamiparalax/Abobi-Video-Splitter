# Random Video Splitter

## Overview
The **Random Video Splitter** is a Python script that splits video files into 60-second clips. It excludes the first and last 2 minutes of each video, ensuring the selection of random segments within the specified timeframe. The script is designed to use the H.265 codec for video and AAC for audio, while also applying custom metadata to each clip.

## Features
- Excludes the first and last 2 minutes of the video.
- Randomly selects 60-second clips.
- Uses H.265 codec for video compression and AAC for audio.
- Applies custom metadata (artist, album, comment, date).
- Allows the user to select a folder and specify the number of files to split.

## Prerequisites
- Python 3.6 or higher.
- `ffmpeg` installed and available in the system's PATH.
- Required Python packages listed in `requirements.txt`.

## Installation
1. Clone this repository:
    ```bash
    git clone <repository-url>
    cd Random-Video-Splitter
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. Run the script:
    ```bash
    python Random-Video-Splitter.py
    ```
2. Select the folder containing the video files.
3. Specify the number of files to split.
4. The output clips will be saved in the selected output folder.

## Example
![screenshot](screenshot.png)
*Screenshot showing the script in action.*

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributions
Feel free to fork this repository and submit pull requests if you'd like to contribute.

## Issues
If you encounter any problems, please open an issue in the [issue tracker](https://github.com/YamiParalax/Random-Video-Splitter/issues).
