import sqlite3
import os
from typing import Optional, List, Tuple, Any


class DatabaseManager:
    """Quản lý kết nối và thao tác với SQLite database"""
    
    def __init__(self, db_path: str = "data/student_management.db"):
        """
        Khởi tạo database manager
        
        Args:
            db_path: Đường dẫn đến file database
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._ensure_data_directory()
        self._init_database()
    
    def _ensure_data_directory(self):
        """Tạo thư mục data nếu chưa tồn tại"""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def connect(self) -> sqlite3.Connection:
        """
        Tạo kết nối đến database
        
        Returns:
            Connection object
        """
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Cho phép truy cập cột theo tên
        return self.connection
    
    def disconnect(self):
        """Đóng kết nối database"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def _init_database(self):
        """Khởi tạo các bảng trong database"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Bảng User (base table cho Student, Lecturer, Admin)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                role TEXT NOT NULL CHECK(role IN ('student', 'lecturer', 'admin')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Bảng Student
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                date_of_birth DATE,
                major TEXT,
                enrollment_year INTEGER,
                gpa REAL DEFAULT 0.0,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Bảng Lecturer
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lecturers (
                lecturer_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                department TEXT,
                specialization TEXT,
                hire_date DATE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Bảng Admin
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                admin_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                permission_level INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Bảng Course
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                credits INTEGER NOT NULL CHECK(credits > 0),
                prerequisite TEXT,
                description TEXT,
                max_students INTEGER DEFAULT 50,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prerequisite) REFERENCES courses(course_id)
            )
        ''')
        
        # Bảng Schedule
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id TEXT NOT NULL,
                lecturer_id TEXT NOT NULL,
                semester TEXT NOT NULL,
                year INTEGER NOT NULL,
                day_of_week TEXT CHECK(day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                room TEXT,
                FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
                FOREIGN KEY (lecturer_id) REFERENCES lecturers(lecturer_id)
            )
        ''')
        
        # Bảng Enrollment
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_id TEXT NOT NULL,
                schedule_id INTEGER NOT NULL,
                enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'registered' CHECK(status IN ('registered', 'completed', 'dropped', 'failed')),
                grade REAL,
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
                FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id),
                UNIQUE(student_id, course_id)
            )
        ''')
        
        # Bảng Notification
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT DEFAULT 'info' CHECK(type IN ('info', 'warning', 'success', 'error')),
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Tạo các index để tối ưu truy vấn
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments(student_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedules_course ON schedules(course_id)')
        
        conn.commit()
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """
        Thực thi SELECT query
        
        Args:
            query: SQL query
            params: Tham số cho query
            
        Returns:
            List các row kết quả
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """
        Thực thi INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL query
            params: Tham số cho query
            
        Returns:
            Số row bị ảnh hưởng
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Thực thi batch INSERT/UPDATE
        
        Args:
            query: SQL query
            params_list: List các tuple tham số
            
        Returns:
            Số row bị ảnh hưởng
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        return cursor.rowcount
    
    def get_last_insert_id(self) -> int:
        """
        Lấy ID của row vừa insert
        
        Returns:
            Last insert row ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        last_id = cursor.lastrowid
        return last_id if last_id is not None else 0
    
    def begin_transaction(self):
        """Bắt đầu transaction"""
        conn = self.connect()
        conn.execute('BEGIN TRANSACTION')
    
    def commit(self):
        """Commit transaction"""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """Rollback transaction"""
        if self.connection:
            self.connection.rollback()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.disconnect()
