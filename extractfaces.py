import os
import cv2
from pytube import YouTube
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image
import io
import piexif
import shutil
from pytube.exceptions import AgeRestrictedError

def download_youtube_video(url, path='videos'):
    if not os.path.exists(path):
        os.makedirs(path)
    yt = YouTube(url)
    video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    video_stream.download(output_path=path)
    print(f"Video downloaded.")
    return os.path.join(path, video_stream.default_filename)

# This function will be run by multiple processes to handle frame face detection
def is_likely_face(x, y, w, h):
    # Example heuristic: Check if the width and height of the detected box are roughly similar.
    aspect_ratio = w / float(h)
    return 0.75 < aspect_ratio < 1.3

# Modify the 'process_frame' function
def process_frame(frame_data):
    frame_count, frame, face_cascade_path, output_folder, yt_url, yt_title = frame_data
    face_cascade = cv2.CascadeClassifier(face_cascade_path)

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # Save likely faces with EXIF data
    face_filenames = []
    for (x, y, w, h) in faces:
        if not is_likely_face(x, y, w, h):
            continue
        face_img = frame[y:y+h, x:x+w]
        face_filename = f"{output_folder}/face_{frame_count}_{x}_{y}.jpg"

        # Convert the BGR image to RGB
        face_img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image
        im_pil = Image.fromarray(face_img_rgb)

        # Prepare EXIF data
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Make: "YouTube Video",
                piexif.ImageIFD.XPComment: yt_url.encode('utf-16'),
                piexif.ImageIFD.XPTitle: yt_title.encode('utf-16')
            },
        }
        exif_bytes = piexif.dump(exif_dict)

        # Save image with EXIF data
        im_pil.save(face_filename, "jpeg", exif=exif_bytes)

        face_filenames.append(face_filename)
    
    return face_filenames

def extract_faces_from_video(video_path, yt_url, yt_title, output_folder='faces', skip_frames=30, num_workers=4):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

    # Read the video
    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    # Set up a process pool and task queue
    frames_to_process = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_frame = {}
        
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                break
            
            # Skip frames
            if frame_count % skip_frames == 0:
                # Ensure yt_url and yt_title are included in the tuple here
                frames_to_process.append((frame_count, frame, face_cascade_path, output_folder, yt_url, yt_title))
            
            frame_count += 1

            # If we have enough frames queued up, send them to the worker processes
            if len(frames_to_process) == num_workers or not ret:
                for frame_data in frames_to_process:
                    # When submitting to the executor, pass all the needed data
                    future = executor.submit(process_frame, frame_data)  # Pass the entire tuple as a single argument
                    future_to_frame[future] = frame_data[0]  # frame count as identifier
                frames_to_process = []

                # As each process completes, handle the results
                for future in as_completed(future_to_frame):
                    frame_number = future_to_frame[future]
                    try:
                        face_filenames = future.result()
                        print(f"Processed frame {frame_number}: {len(face_filenames)} faces found")
                    except Exception as exc:
                        print(f"Frame {frame_number} generated an exception: {exc}")
        
        print(f"Finished extracting all potential faces, moving to a unique folder now...")
        existing_dirs = [d for d in os.listdir(output_folder) if os.path.isdir(os.path.join(output_folder, d)) and d.isdigit()]
        highest_num = max(map(int, existing_dirs), default=0)  # default to 0 if no directories exist
        new_folder_name = str(highest_num + 1).zfill(3)  # increment and zero-pad the folder name
        new_folder_path = os.path.join(output_folder, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)

        # Move all extracted face images to the new folder
        for filename in os.listdir(output_folder):
            if filename.startswith('face_'):
                shutil.move(os.path.join(output_folder, filename), new_folder_path)

        # Create a text file with video information
        info_file_path = os.path.join(new_folder_path, 'video_info.txt')
        with open(info_file_path, 'w') as f:
            f.write(f"Title: {yt_title}\n")
            f.write(f"URL: {yt_url}\n")

        print(f"All faces moved to folder: {new_folder_path}")
        
        # Release the capture
        cap.release()

def main():
    youtube_url = input("Enter the YouTube video URL: ")
    try:
        # Attempt to download the video
        yt = YouTube(youtube_url)
        video_path = download_youtube_video(youtube_url)
        extract_faces_from_video(video_path, youtube_url, yt.title)
    except AgeRestrictedError as e:
        print(f"Error: The video at {youtube_url} is age-restricted. Can't download without logging in.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
