import cv2
import numpy as np
import os
from datetime import datetime

class FaceUtils:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        if not os.path.exists(cascade_path):
            raise FileNotFoundError(f"Cascade file not found at {cascade_path}")
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def extract_feature_vector(self, image_path):
        """Extract LBPH features from a face image"""
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return None

        try:
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                print(f"Failed to read image: {image_path}")
                return None

            faces = self.face_cascade.detectMultiScale(image, 1.3, 5)

            if len(faces) == 0:
                print("No face detected in the image")
                return None

            (x, y, w, h) = faces[0]
            face = image[y:y+h, x:x+w]

            # Resize face for consistency
            face_resized = cv2.resize(face, (200, 200))

            # Convert face to vector using LBPH
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train([face_resized], np.array([0]))  # label is dummy
            hist = recognizer.getHistograms()[0]  # List of 59 floats

            return hist
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            return None

    def save_user_photo(self, filepath, name):
        """Save user's photo to the dataset directory"""
        try:
            user_folder = os.path.join("dataset", name)
            os.makedirs(user_folder, exist_ok=True)
            dest_path = os.path.join(user_folder, f"{name}_passport.jpg")
            
            # Read and write the image
            img = cv2.imread(filepath)
            if img is None:
                print(f"Failed to read image: {filepath}")
                return None
                
            cv2.imwrite(dest_path, img)
            return dest_path
        except Exception as e:
            print(f"Error saving photo: {e}")
            return None

    def compare_faces(self, image, stored_vectors):
        """Compare a face with stored feature vectors"""
        try:
            # Extract features from the current image
            vector = self.extract_feature_vector(image)
            if vector is None:
                return None

            # Compare with stored vectors
            min_distance = float('inf')
            matched_id = None

            for student_id, stored_vector in stored_vectors.items():
                distance = self.calculate_distance(vector, stored_vector)
                if distance < min_distance:
                    min_distance = distance
                    matched_id = student_id

            # Return match if distance is below threshold
            threshold = 0.6  # Adjust this value based on testing
            return matched_id if min_distance < threshold else None
        except Exception as e:
            print(f"Error comparing faces: {str(e)}")
            return None

    def calculate_distance(self, vector1, vector2):
        """Calculate Euclidean distance between two feature vectors"""
        try:
            return np.sqrt(np.sum((np.array(vector1) - np.array(vector2)) ** 2))
        except Exception as e:
            print(f"Error calculating distance: {str(e)}")
            return float('inf')

    def capture_face(self):
        """Capture face from webcam"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Failed to open webcam")
                return None

            # Create temp directory if it doesn't exist
            os.makedirs("temp", exist_ok=True)
            temp_path = os.path.join("temp", f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to capture frame")
                    break

                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

                # Draw rectangle around face
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                cv2.imshow('Capture Face - Press SPACE when ready', frame)

                key = cv2.waitKey(1)
                if key == 32:  # SPACE key
                    if len(faces) > 0:
                        cv2.imwrite(temp_path, frame)
                        break
                elif key == 27:  # ESC key
                    temp_path = None
                    break

            cap.release()
            cv2.destroyAllWindows()
            return temp_path
        except Exception as e:
            print(f"Error capturing face: {str(e)}")
            if 'cap' in locals():
                cap.release()
            cv2.destroyAllWindows()
            return None 