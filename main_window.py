import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import shutil
import os
import cv2
import re
import numpy as np
import mysql.connector
from datetime import datetime
from .admin_panel import AdminPanel

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AttendEase Application")
        self.configure(bg="LightCyan2")
        self.geometry("800x700")
        self.resizable(False, False)
        
        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": "Mysql@1998",
            "database": "attendease",
            "auth_plugin": 'mysql_native_password'
        }

        # Create tables if they don't exist
        self.setup_database()
        
        # Admin credentials
        self.admin_username = "admin_geu"
        self.admin_password = "facemates"
        self.is_admin_logged_in = False
        
        self.setup_ui()
        self.setup_directories()

    def setup_database(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Create student table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS student (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    student_id VARCHAR(8) UNIQUE NOT NULL,
                    department VARCHAR(50) NOT NULL,
                    gender VARCHAR(10) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    feature_vector LONGTEXT NOT NULL
                )
            """)
            
            # Create attendance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(8) NOT NULL,
                    date DATE NOT NULL,
                    time TIME NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES student(student_id)
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("Database setup completed successfully")
            
        except mysql.connector.Error as err:
            print(f"Database setup error: {err}")
            messagebox.showerror("Database Error", f"Error setting up database: {str(err)}")

    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        directories = ['dataset', 'temp']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def setup_ui(self):
        # Sidebar Frame
        self.sidebar = tk.Frame(self, width=250, bg="LightCyan3")
        self.sidebar.pack(side="left", fill="y")

        # Main Frame (for changing views)
        self.main_frame = tk.Frame(self, bg="LightCyan2")
        self.main_frame.pack(side="right", expand=True, fill="both")

        # Frames Dictionary for Views
        self.frames = {}

        # Registration Frame
        self.register_frame = tk.Frame(self.main_frame, bg="LightCyan2")
        self.register_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.frames["register"] = self.register_frame

        # Attendance Frame
        self.attendance_frame = tk.Frame(self.main_frame, bg="LightCyan2")
        self.attendance_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.frames["attendance"] = self.attendance_frame

        # Admin Login Frame
        self.admin_login_frame = tk.Frame(self.main_frame, bg="LightCyan2")
        self.admin_login_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.frames["admin_login"] = self.admin_login_frame

        # Admin Panel Frame (initially hidden)
        self.admin_frame = AdminPanel(self.main_frame)
        self.admin_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.frames["admin"] = self.admin_frame

        # Sidebar Buttons
        tk.Label(self.sidebar, text="Menu", font=("Georgia", 30, "bold"), bg="LightCyan3").pack(pady=20)

        tk.Button(self.sidebar, text="New Registration", font=("Georgia", 15, "bold"),
                 command=lambda: self.show_frame("register"), bg="lightblue").pack(pady=20, fill="x")
        tk.Button(self.sidebar, text="Check Attendance", font=("Georgia", 15, "bold"),
                 command=lambda: self.show_frame("attendance"), bg="lightblue").pack(pady=20, fill="x")
        tk.Button(self.sidebar, text="Admin Panel", font=("Georgia", 15, "bold"),
                 command=lambda: self.show_frame("admin_login"), bg="lightblue").pack(pady=20, fill="x")

        # Setup Registration UI
        self.setup_registration_ui()
        
        # Setup Attendance UI
        self.setup_attendance_ui()

        # Setup Admin Login UI
        self.setup_admin_login_ui()

        # Show default frame
        self.show_frame("register")

    def setup_registration_ui(self):
        self.photo_path = tk.StringVar()
        self.gender_var = tk.StringVar(value="Male")

        # Title
        registration_label = tk.Label(self.register_frame, text="AttendEase", font=("Georgia", 30, "bold"), bg="LightCyan2")
        registration_label.grid(row=0, column=1, pady=20)

        # Registration Form
        tk.Label(self.register_frame, text="Full Name:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.name_entry = tk.Entry(self.register_frame, font=("Helvetica", 11))
        self.name_entry.grid(row=1, column=1, padx=10)

        tk.Label(self.register_frame, text="Student ID:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.id_entry = tk.Entry(self.register_frame, font=("Helvetica", 11))
        self.id_entry.grid(row=2, column=1, padx=10)

        tk.Label(self.register_frame, text="Department:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.dept_combo = ttk.Combobox(self.register_frame, values=["CSE", "ECE", "ME", "CE", "Other"])
        self.dept_combo.grid(row=3, column=1, padx=10)
        self.dept_combo.current(0)

        tk.Label(self.register_frame, text="Gender:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=4, column=0, padx=10, pady=10, sticky='w')
        tk.Radiobutton(self.register_frame, text="Male", variable=self.gender_var, value="Male", bg="LightCyan2").grid(row=4, column=1, sticky='w')
        tk.Radiobutton(self.register_frame, text="Female", variable=self.gender_var, value="Female", bg="LightCyan2").grid(row=4, column=1, sticky='e')

        tk.Label(self.register_frame, text="Password:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=5, column=0, padx=10, pady=10, sticky='w')
        self.pass_entry = tk.Entry(self.register_frame, font=("Helvetica", 11))
        self.pass_entry.grid(row=5, column=1, padx=10)

        # Upload Photo Button
        tk.Button(self.register_frame, text="Upload Passport Photo", command=self.upload_photo,
                 bg="RoyalBlue1", font=("Helvetica", 11, "bold")).grid(row=6, column=1, columnspan=2, pady=10)

        self.img_label = tk.Label(self.register_frame, bg="LightCyan2")
        self.img_label.grid(row=7, column=1, columnspan=2, pady=10)

        # Register Button
        tk.Button(self.register_frame, text="Register", command=self.register_user,
                 bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), padx=20, pady=5).grid(row=8, column=1, columnspan=2, pady=20)

    def setup_attendance_ui(self):
        # Title
        check_label = tk.Label(self.attendance_frame, text="AttendEase", font=("Georgia", 30, "bold"), bg="LightCyan2")
        check_label.grid(row=0, column=1, pady=20)

        # Login Form
        tk.Label(self.attendance_frame, text="Student ID:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.login_id_entry = tk.Entry(self.attendance_frame, font=("Helvetica", 11))
        self.login_id_entry.grid(row=1, column=1, padx=10)

        tk.Label(self.attendance_frame, text="Password:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.login_pass_entry = tk.Entry(self.attendance_frame, show="*", font=("Helvetica", 11))
        self.login_pass_entry.grid(row=2, column=1, padx=10)

        # Login Button
        tk.Button(self.attendance_frame, text="Check Attendance", command=self.check_attendance,
                 bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), padx=20, pady=5).grid(row=3, column=1, columnspan=2, pady=20)

        # Attendance Table
        # Create a frame for the table with a white background
        table_frame = tk.Frame(self.attendance_frame, bg="white")
        table_frame.grid(row=4, column=0, columnspan=2, pady=20, padx=20, sticky='nsew')

        # Configure column weights
        self.attendance_frame.grid_columnconfigure(0, weight=1)
        self.attendance_frame.grid_columnconfigure(1, weight=1)

        # Create the Treeview with specific column widths and centered text
        columns = ('date', 'time', 'status')
        self.attendance_table = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        # Configure column headings with better formatting
        self.attendance_table.heading('date', text='Date')
        self.attendance_table.heading('time', text='Time')
        self.attendance_table.heading('status', text='Status')
        
        # Configure column widths and alignment
        self.attendance_table.column('date', width=150, anchor='center')
        self.attendance_table.column('time', width=150, anchor='center')
        self.attendance_table.column('status', width=100, anchor='center')
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.attendance_table.yview)
        self.attendance_table.configure(yscrollcommand=y_scrollbar.set)
        
        # Pack the table and scrollbar
        self.attendance_table.pack(side='left', fill='both', expand=True)
        y_scrollbar.pack(side='right', fill='y')

    def setup_admin_login_ui(self):
        # Title
        login_label = tk.Label(self.admin_login_frame, text="Admin Login", font=("Georgia", 30, "bold"), bg="LightCyan2")
        login_label.pack(pady=20)

        # Login Frame
        login_frame = tk.Frame(self.admin_login_frame, bg="LightCyan2")
        login_frame.pack(pady=20)

        # Username
        tk.Label(login_frame, text="Username:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=0, column=0, padx=10, pady=10)
        self.admin_username_entry = tk.Entry(login_frame, font=("Helvetica", 11))
        self.admin_username_entry.grid(row=0, column=1, padx=10)

        # Password
        tk.Label(login_frame, text="Password:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=1, column=0, padx=10, pady=10)
        self.admin_password_entry = tk.Entry(login_frame, show="*", font=("Helvetica", 11))
        self.admin_password_entry.grid(row=1, column=1, padx=10)

        # Login Button
        tk.Button(login_frame, text="Login", command=self.verify_admin,
                 bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), padx=20, pady=5).grid(row=2, column=0, columnspan=2, pady=20)

    def verify_admin(self):
        username = self.admin_username_entry.get().strip()
        password = self.admin_password_entry.get().strip()

        if username == self.admin_username and password == self.admin_password:
            self.is_admin_logged_in = True
            self.show_frame("admin")
            # Clear the login fields
            self.admin_username_entry.delete(0, tk.END)
            self.admin_password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Invalid admin credentials")
            self.is_admin_logged_in = False

    def show_frame(self, name):
        if name == "admin" and not self.is_admin_logged_in:
            self.show_frame("admin_login")
            return
        self.frames[name].tkraise()

    def upload_photo(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if filepath:
            self.photo_path.set(filepath)
            load = Image.open(filepath)
            load.thumbnail((150, 150))
            render = ImageTk.PhotoImage(load)
            self.img_label.config(image=render)
            self.img_label.image = render

    def register_user(self):
        name = self.name_entry.get().strip()
        student_id = self.id_entry.get().strip()
        dept = self.dept_combo.get()
        gender = self.gender_var.get()
        passw = self.pass_entry.get().strip()
        filepath = self.photo_path.get()

        if len(passw) < 6:
            messagebox.showerror("Weak Password", "Password must be at least 6 characters long.")
            return

        if not name or not filepath:
            messagebox.showerror("Error", "Please enter all details and upload a photo.")
            return

        if not re.fullmatch(r'[A-Za-z ]+', name):
            messagebox.showerror("Invalid Name", "Name must contain only alphabets and spaces.")
            return

        if not student_id.isdigit() or len(student_id) != 8:
            messagebox.showerror("Invalid ID", "Student ID must be exactly 8 digits.")
            return

        # Extract feature vector
        vector = self.extract_feature_vector(filepath)
        if vector is None:
            messagebox.showerror("Face Error", "No face detected in photo. Please try again.")
            return

        # Save to database
        self.save_to_database(name, student_id, dept, gender, passw, vector)
        messagebox.showinfo("Success", f"{name} registered successfully!")

    def extract_feature_vector(self, image_path):
        try:
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
            
            print(f"Registration: Vector length = {len(vector)}")
            print(f"Registration: First few values = {vector[:5]}")
            
            if len(vector) == 0:
                print("Error: Empty feature vector generated")
                return None
                
            return vector

        except Exception as e:
            print(f"Error extracting feature vector: {e}")
            return None

    def save_to_database(self, name, student_id, dept, gender, passw, vector):
        try:
            # Verify vector is not None and has data
            if vector is None or len(vector) == 0:
                messagebox.showerror("Error", "Invalid feature vector generated")
                return False

            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Convert vector to string without any numpy array formatting
            vector_str = ','.join(f"{x:.8f}" for x in vector)
            print(f"Storing vector of length {len(vector)} for {name}")
            print(f"First few values being stored: {vector[:5]}")
            
            # Verify the string is not empty
            if not vector_str:
                messagebox.showerror("Error", "Empty vector string generated")
                return False
            
            # Check if student_id already exists
            cursor.execute("SELECT COUNT(*) FROM student WHERE student_id = %s", (student_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Student ID already exists")
                return False
            
            # Insert new student
            sql = """INSERT INTO student 
                     (name, student_id, department, gender, password, feature_vector) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            values = (name, student_id, dept, gender, passw, vector_str)
            
            cursor.execute(sql, values)
            conn.commit()
            
            # Verify the data was stored correctly
            cursor.execute("SELECT feature_vector FROM student WHERE student_id = %s", (student_id,))
            stored_vector = cursor.fetchone()[0]
            print(f"Verified stored vector length: {len(stored_vector.split(','))}")
            
            cursor.close()
            conn.close()
            return True
            
        except mysql.connector.Error as err:
            print(f"Database Error: {err}")
            messagebox.showerror("Database Error", str(err))
            return False
        except Exception as e:
            print(f"Error saving to database: {e}")
            messagebox.showerror("Error", f"Error saving to database: {str(e)}")
            return False

    def check_attendance(self):
        student_id = self.login_id_entry.get().strip()
        password = self.login_pass_entry.get().strip()

        if not student_id or not password:
            messagebox.showerror("Error", "Please enter both Student ID and Password")
            return

        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()

            # First verify student credentials
            cursor.execute("SELECT name FROM student WHERE student_id = %s AND password = %s", 
                         (student_id, password))
            result = cursor.fetchone()

            if result:
                student_name = result[0]
                # Get attendance records with properly formatted date and time
                cursor.execute("""
                    SELECT DATE_FORMAT(date, '%d-%m-%Y') as formatted_date, 
                           TIME_FORMAT(time, '%I:%i %p') as formatted_time, 
                           status 
                    FROM attendance 
                    WHERE student_id = %s 
                    ORDER BY date DESC, time DESC
                """, (student_id,))
                
                records = cursor.fetchall()

                # Clear previous records
                for item in self.attendance_table.get_children():
                    self.attendance_table.delete(item)

                if records:
                    # Add records to table
                    for date, time, status in records:
                        self.attendance_table.insert('', tk.END, values=(date, time, status))
                    messagebox.showinfo("Success", f"Showing attendance records for {student_name}")
                else:
                    messagebox.showinfo("No Records", f"No attendance records found for {student_name}")
            else:
                messagebox.showerror("Error", "Invalid Student ID or Password")

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            print(f"Database Error: {str(err)}")
            messagebox.showerror("Database Error", str(err))
        except Exception as e:
            print(f"Error checking attendance: {str(e)}")
            messagebox.showerror("Error", f"Error checking attendance: {str(e)}") 