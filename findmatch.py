import face_recognition
import os
from multiprocessing import Pool

# Load the image of the person we want to find similar to
reference_image_path = 'example.jpg'
reference_image = face_recognition.load_image_file(reference_image_path)
reference_face_encoding = face_recognition.face_encodings(reference_image)[0]

# Folder containing subfolders with faces
faces_folder_path = 'faces'

matches = []
tolerance = 0.5  # Adjust tolerance according to your requirements, lower equals better but don't over adjust

# Function to find matches in a single image
def find_match_in_image(image_path):
    try:
        # Load each image file and get face encodings
        current_image = face_recognition.load_image_file(image_path)
        current_face_encodings = face_recognition.face_encodings(current_image)
        for face_encoding in current_face_encodings:
            # Compare faces and see if they match
            results = face_recognition.compare_faces([reference_face_encoding], face_encoding, tolerance=tolerance)
            if results[0]:
                return image_path
    except Exception as e:
        print(f"Error processing file {image_path}: {e}")
    return None

# Change the find_matches function to use multiprocessing
def find_matches(folder_path):
    image_paths = []
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith(('jpg', 'jpeg', 'png')):
                image_paths.append(os.path.join(root, filename))

    with Pool() as pool:
        results = pool.map(find_match_in_image, image_paths)

    for result in filter(None, results):
        matches.append(result)

# Start the recursive search
find_matches(faces_folder_path)

# Output the results
print("Matches found:")
for match in matches:
    print(match)
