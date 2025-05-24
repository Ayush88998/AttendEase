import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime

class AttendanceFrame(tk.Frame):
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

    def setup_ui(self):
        # Title
        title_label = tk.Label(self, text="AttendEase", font=("Georgia", 30, "bold"), bg="LightCyan2")
        title_label.pack(pady=20)

        # Login Frame
        login_frame = tk.Frame(self, bg="LightCyan2")
        login_frame.pack(pady=20)

        # Student ID
        tk.Label(login_frame, text="Student ID:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=0, column=0, padx=10, pady=10)
        self.id_entry = tk.Entry(login_frame, font=("Helvetica", 11))
        self.id_entry.grid(row=0, column=1, padx=10)

        # Password
        tk.Label(login_frame, text="Password:", bg="LightCyan2", font=("Helvetica", 11, "bold")).grid(row=1, column=0, padx=10, pady=10)
        self.pass_entry = tk.Entry(login_frame, show="*", font=("Helvetica", 11))
        self.pass_entry.grid(row=1, column=1, padx=10)

        # Login Button
        tk.Button(login_frame, text="Login", command=self.login, bg="#4CAF50", fg="white", 
                 font=("Helvetica", 12, "bold"), padx=20, pady=5).grid(row=2, column=0, columnspan=2, pady=20)

        # Attendance Display Frame (initially hidden)
        self.attendance_frame = tk.Frame(self, bg="LightCyan2")
        
        # Create Treeview for attendance records
        columns = ('date', 'time', 'status')
        self.attendance_table = ttk.Treeview(self.attendance_frame, columns=columns, show='headings', height=10)
        
        # Define headings
        self.attendance_table.heading('date', text='Date')
        self.attendance_table.heading('time', text='Time')
        self.attendance_table.heading('status', text='Status')
        
        # Define columns
        self.attendance_table.column('date', width=150, anchor='center')
        self.attendance_table.column('time', width=150, anchor='center')
        self.attendance_table.column('status', width=150, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.attendance_frame, orient=tk.VERTICAL, command=self.attendance_table.yview)
        self.attendance_table.configure(yscrollcommand=scrollbar.set)
        
        # Pack the table and scrollbar
        self.attendance_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=20, padx=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def login(self):
        student_id = self.id_entry.get().strip()
        password = self.pass_entry.get().strip()

        if not student_id or not password:
            messagebox.showerror("Error", "Please enter both Student ID and Password")
            return

        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()

            # Check credentials
            cursor.execute("SELECT name FROM student WHERE student_id = %s AND password = %s",
                         (student_id, password))
            result = cursor.fetchone()

            if result:
                self.show_attendance(student_id, result[0])
            else:
                messagebox.showerror("Error", "Invalid Student ID or Password")

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def show_attendance(self, student_id, name):
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()

            # Get attendance records
            cursor.execute("""
                SELECT date, time, status 
                FROM attendance 
                WHERE student_id = %s 
                ORDER BY date DESC, time DESC
            """, (student_id,))
            records = cursor.fetchall()

            # Clear previous records
            for item in self.attendance_table.get_children():
                self.attendance_table.delete(item)
            
            # Add records to table
            for date, time, status in records:
                self.attendance_table.insert('', tk.END, values=(date, time, status))

            # Show attendance frame
            self.attendance_frame.pack(pady=20)

            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        
        