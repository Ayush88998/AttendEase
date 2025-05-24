import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
import mysql.connector
from datetime import datetime
import os

class AdminPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="LightCyan2")
        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": "Mysql@1998",
            "database": "attendease",
            "auth_plugin": 'mysql_native_password'
        }
        self.setup_ui()
        self.camera = None
        self.is_capturing = False
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.current_frame = None
        self.bind_all('<space>', self.capture_and_process)

    def setup_ui(self):
        # Main container frame
        main_container = tk.Frame(self, bg="LightCyan2")
        main_container.pack(expand=True, fill="both", padx=20, pady=20)

        # Title Frame
        title_frame = tk.Frame(main_container, bg="LightCyan2")
        title_frame.pack(fill="x", pady=(0, 20))

        # Title
        title_label = tk.Label(title_frame, text="Face Attendance System", 
                             font=("Georgia", 24, "bold"), bg="LightCyan2")
        title_label.pack()

        # Instructions Label
        instructions_label = tk.Label(title_frame, 
                                   text="Press SPACE to capture and process face",
                                   font=("Helvetica", 12), bg="LightCyan2")
        instructions_label.pack(pady=(5, 0))

        # Camera Frame
        self.camera_frame = tk.Frame(main_container, bg="LightCyan2")
        self.camera_frame.pack(pady=10)

        # Video Label with border
        video_container = tk.Frame(self.camera_frame, bg="black", padx=2, pady=2)
        video_container.pack()
        
        self.video_label = tk.Label(video_container, bg="black")
        self.video_label.pack()

        # Control Buttons Frame
        control_frame = tk.Frame(main_container, bg="LightCyan2")
        control_frame.pack(pady=20)

        # Start/Stop Button
        self.toggle_button = tk.Button(control_frame, text="Start Camera", 
                                     command=self.toggle_camera,
                                     bg="#4CAF50", fg="white", 
                                     font=("Helvetica", 12, "bold"), 
                                     padx=20, pady=5)
        self.toggle_button.pack(side=tk.LEFT, padx=10)

        # Status Label
        self.status_label = tk.Label(control_frame, text="Camera: Off", 
                                   bg="LightCyan2", font=("Helvetica", 11))
        self.status_label.pack(side=tk.LEFT, padx=10)

    def toggle_camera(self):
        if not self.is_capturing:
            self.start_camera()
        else:
            self.stop_camera()

    def start_camera(self):
        self.camera = cv2.VideoCapture(0)
        self.is_capturing = True
        self.toggle_button.config(text="Stop Camera")
        self.status_label.config(text="Camera: On")
        self.update_camera()

    def stop_camera(self):
        self.is_capturing = False
        if self.camera is not None:
            self.camera.release()
        self.toggle_button.config(text="Start Camera")
        self.status_label.config(text="Camera: Off")
        self.video_label.config(image='')

    def update_camera(self):
        if self.is_capturing:
            ret, frame = self.camera.read()
            if ret:
                # Store the current frame
                self.current_frame = frame.copy()
                
                # Convert frame to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

                # Draw rectangle around faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame_rgb, (x, y), (x+w, y+h), (0, 255, 0), 2)

                # Resize frame to fit the window
                height, width = frame_rgb.shape[:2]
                max_height = 400  # Maximum height for the video feed
                if height > max_height:
                    scale = max_height / height
                    width = int(width * scale)
                    height = max_height
                    frame_rgb = cv2.resize(frame_rgb, (width, height))

                # Convert to PhotoImage
                image = Image.fromarray(frame_rgb)
                image = ImageTk.PhotoImage(image)
                
                # Update video label
                self.video_label.config(image=image)
                self.video_label.image = image

                # Schedule next update
                self.after(10, self.update_camera)

    def capture_and_process(self, event):
        if not self.is_capturing or self.current_frame is None:
            return

        # Convert frame to grayscale
        gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            messagebox.showwarning("No Face Detected", "Please position your face in front of the camera")
            return

        # Process the first detected face
        (x, y, w, h) = faces[0]
        face = gray[y:y+h, x:x+w]
        self.process_face(face)

    def process_face(self, face):
        try:
            # Resize face for consistency
            face_resized = cv2.resize(face, (200, 200))
            
            # Extract feature vector using LBPH
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train([face_resized], np.array([0]))
            histograms = recognizer.getHistograms()
            current_vector = np.array(histograms[0][0], dtype=np.float64)  # Get first histogram's data
            
            print(f"Current vector length: {len(current_vector)}")
            print(f"Current vector first few values: {current_vector[:5]}")

            # Connect to database
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()

            # Get all student feature vectors
            cursor.execute("SELECT student_id, name, feature_vector FROM student")
            students = cursor.fetchall()

            # Compare with stored vectors
            best_match = None
            best_similarity = float('inf')
            
            for student_id, name, stored_vector_str in students:
                try:
                    # Split the string by comma and convert to float array
                    stored_vector = np.array([float(x) for x in stored_vector_str.split(',')])
                    
                    print(f"Processing {name}:")
                    print(f"  Stored vector length: {len(stored_vector)}")
                    print(f"  Stored vector first few values: {stored_vector[:5]}")
                    
                    # Ensure vectors are of same length
                    if len(stored_vector) != len(current_vector):
                        print(f"  Vector length mismatch: stored={len(stored_vector)}, current={len(current_vector)}")
                        continue
                    
                    # Calculate cosine similarity
                    dot_product = np.dot(current_vector, stored_vector)
                    norm_product = np.linalg.norm(current_vector) * np.linalg.norm(stored_vector)
                    similarity = 1 - (dot_product / norm_product)  # Convert to distance (0 is perfect match)
                    
                    print(f"  Similarity score: {similarity}")
                    
                    # Keep track of best match
                    if similarity < best_similarity:
                        best_similarity = similarity
                        best_match = (student_id, name)
                    
                except Exception as e:
                    print(f"Error processing vector for {name}: {str(e)}")
                    print(f"Stored vector string: {stored_vector_str[:100]}...")  # Print first 100 chars
                    continue

            # Check if we found a good match
            if best_match and best_similarity < 0.8:  # Threshold for cosine similarity distance
                print(f"Best match found: {best_match[1]} with similarity {best_similarity}")
                self.mark_attendance(*best_match)
            else:
                print(f"No good match found. Best similarity was {best_similarity}")
                messagebox.showinfo("No Match", "No matching face found in database")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"Error processing face: {str(e)}")
            messagebox.showerror("Processing Error", f"Error processing face: {str(e)}")

    def mark_attendance(self, student_id, name):
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()

            # Check if attendance already marked for today
            current_date = datetime.now().date()
            cursor.execute("""
                SELECT COUNT(*) FROM attendance 
                WHERE student_id = %s AND DATE(date) = %s
            """, (student_id, current_date))
            
            if cursor.fetchone()[0] == 0:
                # Mark attendance
                current_time = datetime.now().time()
                cursor.execute("""
                    INSERT INTO attendance 
                    (student_id, date, time, status)
                    VALUES (%s, %s, %s, %s)
                """, (student_id, current_date, current_time, "Present"))
                conn.commit()
                messagebox.showinfo("Success", f"Attendance marked for {name}")
            else:
                messagebox.showinfo("Already Marked", f"Attendance already marked for {name} today")

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            print(f"Database Error: {str(err)}")
            messagebox.showerror("Database Error", str(err))
        except Exception as e:
            print(f"Error marking attendance: {str(e)}")
            messagebox.showerror("Error", f"Error marking attendance: {str(e)}")

    def extract_feature_vector(self, image_path):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        faces = face_cascade.detectMultiScale(image, 1.3, 5)

        if len(faces) == 0:
            return None

        (x, y, w, h) = faces[0]
        face = image[y:y+h, x:x+w]
        face_resized = cv2.resize(face, (200, 200))

        # Extract feature vector using LBPH
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train([face_resized], np.array([0]))
        histograms = recognizer.getHistograms()
        vector = np.array(histograms[0][0], dtype=np.float64)  # Get first histogram's data
        
        # Convert to a simple comma-separated string
        vector_str = ','.join(f"{x:.8f}" for x in vector)
        print(f"Extracted vector length: {len(vector)}")
        print(f"First few values of extracted vector: {vector[:5]}")
        
        return vector_str

    def __del__(self):
        if self.camera is not None:
            self.camera.release() 