"""Enrollment model"""
from datetime import datetime
from typing import Literal
from ..database.db_manager import DatabaseManager as DBManager

class Enrollment:
    def __init__(self, course_id, student_id, semester: int, year: int,
                 status: Literal['registered', 'completed', 'dropped', 'failed'], 
                 process_grade: float = 0.0, final_grade: float = 0.0, 
                 grade: float = 0.0, GPA = 0.0):
        self.course_id = course_id
        self.student_id = student_id
        self.semester = semester
        self.year = year
        self.status = status
        self.process_grade = process_grade
        self.final_grade = final_grade
        self.grade = grade
        self.GPA = GPA

    @staticmethod
    def get_completed_courses(student_id: str, db: DBManager) -> list:
        query = "SELECT course_id FROM enrollments WHERE student_id = ? AND status = 'completed'"
        rows = db.execute_query(query, (student_id,))
        return [row['course_id'] for row in rows]
