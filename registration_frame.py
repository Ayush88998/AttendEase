import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import re
import os
from ..database.db_operations import DatabaseManager
from ..utils.face_utils import FaceUtils

class RegistrationFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="LightCyan2")
        self.db_manager = DatabaseManager()
        self.face_utils = FaceUtils()
        self.photo_path = tk.StringVar()
        self.gender_var = tk.StringVar(value="Male")
        
        # Configure grid weights
        self.grid_rowconfigure(8, weight=1)  # Extra space at bottom
        self.grid_columnconfigure(1, weight=1)  # Form fields expand
        
        self.setup_ui()

    def setup_ui(self):
        # Create a frame for the form
        form_frame = tk.Frame(self, bg="LightCyan2")
        form_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=20)
        
        # Center the form
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        registration_label = tk.Label(form_frame, text="AttendEase", font=("Georgia", 30, "bold"), bg="LightCyan2")
        registration_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Name
        tk.Label(form_frame, text="Full Name:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.name_entry = tk.Entry(form_frame, font=("Helvetica", 11))
        self.name_entry.grid(row=1, column=1, padx=10, sticky='ew')

        # Student ID
        tk.Label(form_frame, text="Student ID:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.id_entry = tk.Entry(form_frame, font=("Helvetica", 11))
        self.id_entry.grid(row=2, column=1, padx=10, sticky='ew')

        # Department
        tk.Label(form_frame, text="Department:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.dept_combo = ttk.Combobox(form_frame, values=["CSE", "ECE", "ME", "CE", "Other"])
        self.dept_combo.grid(row=3, column=1, padx=10, sticky='ew')
        self.dept_combo.current(0)

        # Gender
        gender_frame = tk.Frame(form_frame, bg="LightCyan2")
        gender_frame.grid(row=4, column=1, sticky='ew', padx=10)
        
        tk.Label(form_frame, text="Gender:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=4, column=0, padx=10, pady=10, sticky='w')
        tk.Radiobutton(gender_frame, text="Male", variable=self.gender_var, value="Male", bg="LightCyan2").pack(side='left', padx=10)
        tk.Radiobutton(gender_frame, text="Female", variable=self.gender_var, value="Female", bg="LightCyan2").pack(side='left', padx=10)

        # Password
        tk.Label(form_frame, text="Password:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=5, column=0, padx=10, pady=10, sticky='w')
        self.pass_entry = tk.Entry(form_frame, font=("Helvetica", 11), show="*")
        self.pass_entry.grid(row=5, column=1, padx=10, sticky='ew')

        # Photo Upload
        photo_frame = tk.Frame(form_frame, bg="LightCyan2")
        photo_frame.grid(row=6, column=0, columnspan=2, pady=20, sticky='ew')
        
        tk.Button(photo_frame, text="Upload Passport Photo", command=self.upload_photo, 
                 bg="RoyalBlue1", font=("Helvetica", 11, "bold")).pack(pady=10)
        
        self.img_label = tk.Label(photo_frame, bg="LightCyan2")
        self.img_label.pack(pady=10)

        # Register Button
        tk.Button(form_frame, text="Register", command=self.register_user, 
                 bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), 
                 padx=40, pady=10).grid(row=8, column=0, columnspan=2, pady=20)

    def upload_photo(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if filepath:
            self.photo_path.set(filepath)
            load = Image.open(filepath)
            load.thumbnail((150, 150))
            render = ImageTk.PhotoImage(load)
            self.img_label.config(image=render)
            self.img_label.image = render

    def validate_inputs(self):
        name = self.name_entry.get().strip()
        student_id = self.id_entry.get().strip()
        passw = self.pass_entry.get().strip()

        if not name or not self.photo_path.get():
            messagebox.showerror("Error", "Please enter all details and upload a photo.")
            return False

        if not re.fullmatch(r'[A-Za-z ]+', name):
            messagebox.showerror("Invalid Name", "Name must contain only alphabets and spaces.")
            return False

        if not student_id.isdigit() or len(student_id) != 8:
            messagebox.showerror("Invalid ID", "Student ID must be exactly 8 digits.")
            return False

        if len(passw) < 6:
            messagebox.showerror("Weak Password", "Password must be at least 6 characters long.")
            return False

        return True

    def register_user(self):
        if not self.validate_inputs():
            return

        name = self.name_entry.get().strip()
        student_id = self.id_entry.get().strip()
        dept = self.dept_combo.get()
        gender = self.gender_var.get()
        passw = self.pass_entry.get().strip()
        filepath = self.photo_path.get()

        # Extract feature vector
        vector = self.face_utils.extract_feature_vector(filepath)
        if vector is None:
            messagebox.showerror("Face Error", "No face detected in photo. Please try again.")
            return

        # Save to database
        if self.db_manager.save_student(name, student_id, dept, gender, passw, vector):
            messagebox.showinfo("Success", f"{name} registered successfully!")
            self.clear_form()

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.id_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.dept_combo.current(0)
        self.gender_var.set("Male")
        self.photo_path.set("")
        self.img_label.config(image="") 