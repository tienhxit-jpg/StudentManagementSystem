class Student:
    MAX_CREDITS = 18

    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.registered_courses = []
        self.completed_courses = []

    # Tính tổng số tín chỉ đã đăng ký
    def total_credits(self):
        return sum(course.credits for course in self.registered_courses)

    # Kiểm tra điều kiện đăng ký môn học
    def can_register(self, course):
        # kiểm tra tín chỉ tối đa
        if self.total_credits() + course.credits > self.MAX_CREDITS:
            return False

        # kiểm tra môn tiên quyết
        for pre in course.prerequisites:
            if pre not in self.completed_courses:
                return False

        return True

    # Đăng ký môn học
    def register_course(self, course):
        if self.can_register(course):
            self.registered_courses.append(course)

    # Hủy đăng ký môn học
    def unregister_course(self, course_id):
        self.registered_courses = [
            c for c in self.registered_courses
            if c.course_id != course_id
        ]
