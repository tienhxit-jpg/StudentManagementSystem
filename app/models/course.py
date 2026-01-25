"""Course model"""
from datetime import datetime


def _get_row_value(row, key, default=None):
    """Helper to safely get value from sqlite3.Row"""
    try:
        return row[key] if key in row.keys() else default
    except (KeyError, TypeError):
        return default


class Course:
    def __init__(self, course_id, name, credits, prerequisite=None,
                 description="", max_students=50,
                 process_weight=0.3, final_weight=0.7,
                 register_start_date=None, register_end_date=None):
        self.course_id = course_id
        self.name = name
        self.credits = credits
        self.prerequisite = prerequisite
        self.description = description
        self.max_students = max_students
        self.process_weight = process_weight
        self.final_weight = final_weight
        self.register_start_date = register_start_date
        self.register_end_date = register_end_date

    @staticmethod
    def get_by_id(course_id, db):
        query = "SELECT * FROM courses WHERE course_id = ?"
        rows = db.execute_query(query, (course_id,))
        if rows:
            row = rows[0]
            process_weight = _get_row_value(row, 'process_weight', 0.3)
            final_weight = _get_row_value(row, 'final_weight', 0.7)
            register_start_date = _get_row_value(row, 'register_start_date', None)
            register_end_date = _get_row_value(row, 'register_end_date', None)
            return Course(row['course_id'], row['name'], row['credits'],
                          row['prerequisite'], row['description'],
                          row['max_students'], process_weight, final_weight,
                          register_start_date, register_end_date)
        return None
    
    @staticmethod
    def get_all(db):
        query = "SELECT * FROM courses"
        rows = db.execute_query(query)
        courses = []
        for row in rows:
            process_weight = _get_row_value(row, 'process_weight', 0.3)
            final_weight = _get_row_value(row, 'final_weight', 0.7)
            register_start_date = _get_row_value(row, 'register_start_date', None)
            register_end_date = _get_row_value(row, 'register_end_date', None)
            courses.append(Course(row['course_id'], row['name'], row['credits'],
                                  row['prerequisite'], row['description'],
                                  row['max_students'], process_weight, final_weight,
                                  register_start_date, register_end_date))
        return courses
    
    def is_registration_open(self, current_date):
        """
        Kiểm tra xem môn học có đang mở đăng ký hay không
        
        Args:
            current_date: datetime.date object representing current date
            
        Returns:
            bool: True nếu đang trong thời gian đăng ký, False nếu không
        """
        # Nếu không có thông tin về thời gian đăng ký, mặc định là không mở
        if not self.register_start_date or not self.register_end_date:
            return False
        
        # Convert string to date if needed
        try:
            if isinstance(self.register_start_date, str):
                start_date = datetime.strptime(self.register_start_date, '%Y-%m-%d').date()
            else:
                start_date = self.register_start_date
                
            if isinstance(self.register_end_date, str):
                end_date = datetime.strptime(self.register_end_date, '%Y-%m-%d').date()
            else:
                end_date = self.register_end_date
            
            return start_date <= current_date <= end_date
        except (ValueError, TypeError):
            # Nếu có lỗi khi parse date, mặc định là không mở
            return False


