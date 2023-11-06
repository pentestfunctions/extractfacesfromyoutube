# YouTube Face Extractor

This Python script downloads a YouTube video and extracts faces from the video frames, saving them with metadata in an organized directory structure.
- I have tested it on a 2 hour vlog and it took around 10 minutes to complete. 

![Video]([tktyNzq.mp4](https://github.com/pentestfunctions/extractfacesfromyoutube/raw/main/tktyNzq.mp4))

## Prerequisites

Before running this script, ensure the following libraries and packages are installed:

- OpenCV-Python
- pytube
- PIL
- piexif
- concurrent.futures

If you are running this on a system with a Debian-based Linux distribution, you may also need to install the `libgl1-mesa-glx` package for OpenCV dependencies:

```bash
sudo apt-get install libgl1-mesa-glx
```

## Installation
```bash
git clone https://github.com/pentestfunctions/extractfacesfromyoutube.git
cd extractfacesfromyoutube
pip install -r requirements.txt
```

## Usage
Run the script using Python and follow the on-screen prompt to enter a YouTube URL:
```bash
python extractfaces.py
```

The script will:

1. Download the YouTube video to a local directory.
2. Scan through video frames and detect faces.
3. Save cropped images of detected faces to a specified output folder.
4. Organize detected faces in a folder named with a zero-padded number, incrementing with each script execution.
5. Save a text file with the video's title and URL in the corresponding face folder.
- It will also add the video title and URL as exif data to each image just incase you want to use it that way later.

## Notes
The face detection uses a simple heuristic and may not be accurate for all videos. Adjust the is_likely_face function to improve accuracy if needed.
The script is designed to be run from the command line and does not have a graphical user interface.
For videos that are age-restricted, you will not be able to download them without logging in. The script does not currently support authenticated downloads.
