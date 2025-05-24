import mysql.connector
from tkinter import messagebox
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": "Mysql@1998",
            "auth_plugin": 'mysql_native_password'
        }
        self.setup_database()

    def setup_database(self):
        """Create database and necessary tables if they don't exist"""
        try:
            # First connect without database
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Create database if not exists
            cursor.execute("CREATE DATABASE IF NOT EXISTS attendease")
            cursor.execute("USE attendease")
            
            # Add database to config
            self.db_config["database"] = "attendease"
            
            # Create student table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS student (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    student_id VARCHAR(8) UNIQUE NOT NULL,
                    department VARCHAR(50) NOT NULL,
                    gender VARCHAR(10) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    feature_vector TEXT NOT NULL
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
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("Database setup completed successfully")
        except mysql.connector.Error as err:
            error_msg = f"Database Error: {str(err)}"
            print(error_msg)
            messagebox.showerror("Database Error", error_msg)
            raise

    def execute_query(self, query, values=None):
        """Execute a database query with error handling"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
                
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = None
                
            cursor.close()
            conn.close()
            return result
        except mysql.connector.Error as err:
            error_msg = f"Database Error: {str(err)}"
            print(error_msg)
            messagebox.showerror("Database Error", error_msg)
            return None

    def save_student(self, name, student_id, dept, gender, passw, vector):
        """Save a new student record to the database"""
        try:
            vector_str = ','.join(map(str, vector))
            sql = "INSERT INTO student (name, student_id, department, gender, password, feature_vector) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (name, student_id, dept, gender, passw, vector_str)
            
            return self.execute_query(sql, values) is not None
        except Exception as e:
            print(f"Error saving student: {str(e)}")
            return False

    def verify_credentials(self, student_id, password):
        """Verify student credentials"""
        try:
            sql = "SELECT name FROM student WHERE student_id = %s AND password = %s"
            result = self.execute_query(sql, (student_id, password))
            return result[0][0] if result else None
        except Exception as e:
            print(f"Error verifying credentials: {str(e)}")
            return None

    def get_attendance_records(self, student_id):
        """Get attendance records for a student"""
        try:
            sql = """
                SELECT date, time, status 
                FROM attendance 
                WHERE student_id = %s 
                ORDER BY date DESC, time DESC
            """
            return self.execute_query(sql, (student_id,))
        except Exception as e:
            print(f"Error getting attendance records: {str(e)}")
            return []

    def mark_attendance(self, student_id, status="Present"):
        """Mark attendance for a student"""
        try:
            current_date = datetime.now().date()
            current_time = datetime.now().time()
            
            sql = """
                INSERT INTO attendance (student_id, date, time, status)
                VALUES (%s, %s, %s, %s)
            """
            values = (student_id, current_date, current_time, status)
            
            return self.execute_query(sql, values) is not None
        except Exception as e:
            print(f"Error marking attendance: {str(e)}")
            return False 