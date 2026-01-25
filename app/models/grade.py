"""Grade model - Quản lý điểm của sinh viên"""
from ..database.db_manager import DatabaseManager as DBManager


def _get_row_value(row, key, default=None):
    """
    Helper function to safely get value from sqlite3.Row
    """
    try:
        return row[key] if key in row.keys() else default
    except (KeyError, TypeError):
        return default


class Grade:
    """
    Class quản lý điểm của sinh viên cho từng môn học
    
    Attributes:
        enrollment_id: ID đăng ký môn học
        student_id: ID sinh viên
        course_id: ID môn học
        process_grade: Điểm quá trình (0-10)
        final_grade: Điểm cuối kỳ (0-10)
        total_grade: Điểm tổng kết (0-10)
        letter_grade: Điểm chữ (A+, A, B+, B, C+, C, D+, D, F)
        grade_point: Điểm số để tính GPA (4.0 scale)
        process_weight: Hệ số điểm quá trình (dynamic từ course)
        final_weight: Hệ số điểm cuối kỳ (dynamic từ course)
    """
    
    # Hệ số mặc định (nếu không lấy được từ course)
    DEFAULT_PROCESS_WEIGHT = 0.3  # 30% điểm quá trình
    DEFAULT_FINAL_WEIGHT = 0.7    # 70% điểm cuối kỳ
    
    # Bảng chuyển đổi điểm số sang điểm chữ
    GRADE_SCALE = [
        (9.5, 'A+', 4.0),
        (8.5, 'A', 4.0),
        (8.0, 'B+', 3.5),
        (7.0, 'B', 3.0),
        (6.5, 'C+', 2.5),
        (5.5, 'C', 2.0),
        (5.0, 'D+', 1.5),
        (4.0, 'D', 1.0),
        (0.0, 'F', 0.0),
    ]
    
    def __init__(self, enrollment_id, student_id, course_id, 
                 process_grade=0.0, final_grade=0.0,
                 process_weight=None, final_weight=None):
        self.enrollment_id = enrollment_id
        self.student_id = student_id
        self.course_id = course_id
        self.process_grade = process_grade
        self.final_grade = final_grade
        
        # Sử dụng weight được truyền vào, nếu không thì dùng mặc định
        self.process_weight = process_weight if process_weight is not None else self.DEFAULT_PROCESS_WEIGHT
        self.final_weight = final_weight if final_weight is not None else self.DEFAULT_FINAL_WEIGHT
        
        self.total_grade = self.calculate_total_grade()
        self.letter_grade = self.get_letter_grade()
        self.grade_point = self.get_grade_point()
    
    def calculate_total_grade(self) -> float:
        """
        Tính điểm tổng kết từ điểm quá trình và điểm cuối kỳ
        Sử dụng hệ số động từ course
        
        Returns:
            Điểm tổng kết (0-10), làm tròn 2 chữ số thập phân
        """
        total = (self.process_grade * self.process_weight + 
                 self.final_grade * self.final_weight)
        return round(total, 2)
    
    def get_letter_grade(self) -> str:
        """
        Chuyển đổi điểm số sang điểm chữ
        
        Returns:
            Điểm chữ (A+, A, B+, B, C+, C, D+, D, F)
        """
        for threshold, letter, _ in self.GRADE_SCALE:
            if self.total_grade >= threshold:
                return letter
        return 'F'
    
    def get_grade_point(self) -> float:
        """
        Lấy điểm số để tính GPA (hệ 4.0)
        
        Returns:
            Grade point (0.0 - 4.0)
        """
        for threshold, _, point in self.GRADE_SCALE:
            if self.total_grade >= threshold:
                return point
        return 0.0
    
    def is_passed(self) -> bool:
        """
        Kiểm tra môn học có đạt hay không (>= 4.0)
        
        Returns:
            True nếu đạt, False nếu không đạt
        """
        return self.total_grade >= 4.0
    
    @staticmethod
    def update_grade(enrollment_id: int, process_grade: float, 
                     final_grade: float, db: DBManager) -> bool:
        """
        Cập nhật điểm cho một enrollment
        
        Args:
            enrollment_id: ID đăng ký môn học
            process_grade: Điểm quá trình (0-10)
            final_grade: Điểm cuối kỳ (0-10)
            db: Database manager
            
        Returns:
            True nếu cập nhật thành công, False nếu thất bại
        """
        try:
            # Lấy thông tin enrollment và weight của course
            query = """
                SELECT e.student_id, e.course_id, c.process_weight, c.final_weight
                FROM enrollments e
                JOIN courses c ON e.course_id = c.course_id
                WHERE e.enrollment_id = ?
            """
            rows = db.execute_query(query, (enrollment_id,))
            
            if not rows:
                return False
            
            row = rows[0]
            process_weight = _get_row_value(row, 'process_weight', Grade.DEFAULT_PROCESS_WEIGHT)
            final_weight = _get_row_value(row, 'final_weight', Grade.DEFAULT_FINAL_WEIGHT)
            
            # Tạo grade object để tính toán với weight của course
            grade = Grade(enrollment_id, row['student_id'], row['course_id'],
                         process_grade, final_grade, process_weight, final_weight)
            
            # Cập nhật vào database
            query = """
                UPDATE enrollments 
                SET process_grade = ?, 
                    final_grade = ?, 
                    grade = ?,
                    status = ?
                WHERE enrollment_id = ?
            """
            status = 'completed' if grade.is_passed() else 'failed'
            
            db.execute_update(query, (
                grade.process_grade,
                grade.final_grade,
                grade.total_grade,
                status,
                enrollment_id
            ))
            
            return True
        except Exception as e:
            print(f"Error updating grade: {e}")
            return False
    
    @staticmethod
    def get_student_grades(student_id: str, semester: int, year: int, 
                          db: DBManager) -> list:
        """
        Lấy tất cả điểm của sinh viên trong một học kỳ
        
        Args:
            student_id: ID sinh viên
            semester: Học kỳ (1, 2, 3)
            year: Năm học
            db: Database manager
            
        Returns:
            List các Grade objects
        """
        query = """
            SELECT e.enrollment_id, e.student_id, e.course_id,
                   e.process_grade, e.final_grade, e.grade,
                   c.process_weight, c.final_weight
            FROM enrollments e
            JOIN schedules s ON e.schedule_id = s.schedule_id
            JOIN courses c ON e.course_id = c.course_id
            WHERE e.student_id = ? AND s.semester = ? AND s.year = ?
        """
        rows = db.execute_query(query, (student_id, semester, year))
        
        grades = []
        for row in rows:
            process_weight = _get_row_value(row, 'process_weight', Grade.DEFAULT_PROCESS_WEIGHT)
            final_weight = _get_row_value(row, 'final_weight', Grade.DEFAULT_FINAL_WEIGHT)
            
            grade = Grade(
                row['enrollment_id'],
                row['student_id'],
                row['course_id'],
                row['process_grade'],
                row['final_grade'],
                process_weight,
                final_weight
            )
            grades.append(grade)
        
        return grades
    
    @staticmethod
    def calculate_semester_gpa(student_id: str, semester: int, year: int,
                              db: DBManager) -> float:
        """
        Tính GPA của sinh viên trong một học kỳ
        
        Args:
            student_id: ID sinh viên
            semester: Học kỳ (1, 2, 3)
            year: Năm học
            db: Database manager
            
        Returns:
            GPA (0.0 - 4.0), làm tròn 2 chữ số thập phân
        """
        query = """
            SELECT e.grade, c.credits
            FROM enrollments e
            JOIN schedules s ON e.schedule_id = s.schedule_id
            JOIN courses c ON e.course_id = c.course_id
            WHERE e.student_id = ? AND s.semester = ? AND s.year = ?
            AND e.status IN ('completed', 'failed')
            AND e.grade IS NOT NULL
        """
        rows = db.execute_query(query, (student_id, semester, year))
        
        if not rows:
            return 0.0
        
        total_points = 0.0
        total_credits = 0
        
        for row in rows:
            # Sử dụng điểm tổng kết có sẵn trong database
            total_grade = row['grade']
            
            # Chuyển đổi sang grade point
            grade_point = 0.0
            for threshold, _, point in Grade.GRADE_SCALE:
                if total_grade >= threshold:
                    grade_point = point
                    break
            
            credits = row['credits']
            total_points += grade_point * credits
            total_credits += credits
        
        if total_credits == 0:
            return 0.0
        
        gpa = total_points / total_credits
        return round(gpa, 2)
    
    @staticmethod
    def calculate_cumulative_gpa(student_id: str, db: DBManager) -> float:
        """
        Tính GPA tích lũy của sinh viên (tất cả học kỳ)
        
        Args:
            student_id: ID sinh viên
            db: Database manager
            
        Returns:
            GPA tích lũy (0.0 - 4.0), làm tròn 2 chữ số thập phân
        """
        query = """
            SELECT e.grade, c.credits
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
            WHERE e.student_id = ?
            AND e.status IN ('completed', 'failed')
            AND e.grade IS NOT NULL
        """
        rows = db.execute_query(query, (student_id,))
        
        if not rows:
            return 0.0
        
        total_points = 0.0
        total_credits = 0
        
        for row in rows:
            # Sử dụng điểm tổng kết có sẵn trong database
            total_grade = row['grade']
            
            # Chuyển đổi sang grade point
            grade_point = 0.0
            for threshold, _, point in Grade.GRADE_SCALE:
                if total_grade >= threshold:
                    grade_point = point
                    break
            
            credits = row['credits']
            total_points += grade_point * credits
            total_credits += credits
        
        if total_credits == 0:
            return 0.0
        
        gpa = total_points / total_credits
        return round(gpa, 2)
    
    @staticmethod
    def get_grade_statistics(student_id: str, db: DBManager) -> dict:
        """
        Lấy thống kê điểm của sinh viên
        
        Args:
            student_id: ID sinh viên
            db: Database manager
            
        Returns:
            Dictionary chứa các thống kê
        """
        query = """
            SELECT e.process_grade, e.final_grade, e.grade, e.status, c.credits
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
            WHERE e.student_id = ?
            AND e.status IN ('completed', 'failed')
        """
        rows = db.execute_query(query, (student_id,))
        
        if not rows:
            return {
                'total_courses': 0,
                'passed_courses': 0,
                'failed_courses': 0,
                'total_credits': 0,
                'passed_credits': 0,
                'cumulative_gpa': 0.0,
                'average_grade': 0.0
            }
        
        total_courses = len(rows)
        passed_courses = sum(1 for r in rows if r['grade'] >= 4.0)
        failed_courses = total_courses - passed_courses
        total_credits = sum(r['credits'] for r in rows)
        passed_credits = sum(r['credits'] for r in rows if r['grade'] >= 4.0)
        average_grade = round(sum(r['grade'] for r in rows) / total_courses, 2)
        
        return {
            'total_courses': total_courses,
            'passed_courses': passed_courses,
            'failed_courses': failed_courses,
            'total_credits': total_credits,
            'passed_credits': passed_credits,
            'cumulative_gpa': Grade.calculate_cumulative_gpa(student_id, db),
            'average_grade': average_grade
        }
    
    def __repr__(self) -> str:
        return (f"Grade(Course: {self.course_id}, "
                f"Process: {self.process_grade}, Final: {self.final_grade}, "
                f"Total: {self.total_grade}, Letter: {self.letter_grade}, "
                f"Point: {self.grade_point})")
