import sqlite3
import re
from app.models.enrollment import Enrollment

# ==========================================================
# 1. Unified Student Class (Registration & Grades Logic)
# ==========================================================
class Student:
    MAX_CREDITS = 20  # tín chỉ tối đa theo quy định

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

# =====================================
# 2. Update Personal Profile Function 
# =====================================
def update_student_profile(student_id):
    print(f"\n=== UPDATE STUDENT PROFILE (ID: {student_id}) ===")
    
    # 1. Connect to Database and get current info
    conn = sqlite3.connect('management_system.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Student WHERE studentID = ?", (student_id,))
    row = cursor.fetchone()
    
    if not row:
        print("Error: Student not found.")
        conn.close()
        return

    # 2. Get Input and Check if empty (Step by step)
    
    # --- Full Name ---
    name_input = input(f"Enter new Name (Current: {row['fullName']}): ")
    if name_input == "":
        new_name = row['fullName']
    else:
        new_name = name_input

    # --- Phone Number ---
    phone_input = input(f"Enter new Phone (Current: {row['phone']}): ")
    if phone_input == "":
        new_phone = row['phone']
    else:
        new_phone = phone_input

    # --- Email ---
    email_input = input(f"Enter new Email (Current: {row['email']}): ")
    if email_input == "":
        new_email = row['email']
    else:
        new_email = email_input

    # --- Address ---
    address_input = input(f"Enter new Address (Current: {row['address']}): ")
    if address_input == "":
        new_address = row['address']
    else:
        new_address = address_input

    # 3. Data Validation
    is_valid = True

    # Check Phone: must be exactly 10 digits
    if not (new_phone.isdigit() and len(new_phone) == 10):
        print("Error: Phone number must be exactly 10 digits.")
        is_valid = False

    # Check Email format using re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
        print("Error: Invalid Email format.")
        is_valid = False

    # 4. Save to Database if everything is okay
    if is_valid:
        try:
            cursor.execute("""
                UPDATE Student 
                SET fullName = ?, phone = ?, email = ?, address = ?
                WHERE studentID = ? 
                """, (new_name, new_phone, new_email, new_address, student_id))
            
            conn.commit()
            print("Success: Information updated!")
        except Exception as e:
            print(f"Database Error: {e}")
            
    conn.close()



