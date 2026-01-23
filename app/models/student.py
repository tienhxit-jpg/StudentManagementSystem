class Student:
    MAX_CREDITS = 18  # tín chỉ tối đa theo quy định

    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.registered_courses = []   # danh sách Course đang đăng ký
        self.completed_courses = []    # danh sách course_id đã hoàn thành

    # Tính tổng số tín chỉ đã đăng ký
    def total_credits(self):
        return sum(course.credits for course in self.registered_courses)

    # Kiểm tra điều kiện đăng ký môn học
    def can_register(self, course):
        # Kiểm tra tín chỉ tối đa
        if self.total_credits() + course.credits > self.MAX_CREDITS:
            return False, "Exceed maximum credits"

        # Kiểm tra môn tiên quyết
        if course.prerequisite:
            if course.prerequisite not in self.completed_courses:
                return False, "Prerequisite not completed"

        return True, "Eligible"

    # Đăng ký môn học
    def register_course(self, course):
        # Kiểm tra đã đăng ký chưa
        if course in self.registered_courses:
            raise ValueError("Course already registered")

        ok, message = self.can_register(course)
        if not ok:
            raise ValueError(message)

        self.registered_courses.append(course)

    # Hủy đăng ký môn học
    def cancel_course(self, course_id):
        for course in self.registered_courses:
            if course.course_id == course_id:
                self.registered_courses.remove(course)
                return
        raise ValueError("Course not found in registration list")


# Chức năng xem điểm cho sinh viên
class Student:
    def __init__(self, student_id, fullname):
        self.student_id = student_id
        self.fullname = fullname
        self.enrollments = []  # 0..*

    def view_grades(self):
        if not self.enrollments:
            print("You have no enrolled courses.")
            return

        total_points = 0
        total_credits = 0

        print("===== VIEW GRADES =====")
        for e in self.enrollments:
            c = e.course
            print(f"Course ID   : {c.course_id}")
            print(f"Course Name : {c.course_name}")
            print(f"Credits     : {c.credits}")
            print(f"Semester    : {e.semester}")

            if e.grade is None:
                print("Grade       : Grade not available yet")
            else:
                print(f"Grade       : {e.grade}")
                total_points += e.grade * c.credits
                total_credits += c.credits

            print("------------------------")

        if total_credits > 0:
            print("GPA:", round(total_points / total_credits, 2))
        else:
            print("GPA: Not available")

