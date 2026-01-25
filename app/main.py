import sys
from models import User, Admin, Student, Lecturer, Enrollment, Course, Notification


def main_menu():
    """Mục 8.1: Main Menu"""
    while True:
        print("\n==================================================")
        print("            STUDENT MANAGEMENT SYSTEM             ")
        print("==================================================")
        print("1. Login")
        print("2. View Public Notifications")
        print("3. Exit")
        print("--------------------------------------------------")
        
        selection = input("Selection: ")
        
        if selection == '1':

        elif selection == '2':
        elif selection == '3':
            sys.exit()
        else:
            print("Invalid selection. Please try again.")

def login_process():
    """Quy trình đăng nhập để phân loại Dashboard"""
    print("\n- Login: The system prompts the user to input their ID and Password.")
    user_id = input("Enter ID: ")
    password = input("Enter Password: ")
    
    # Mô phỏng phân quyền dựa trên ID (Trong thực tế sẽ check database)
    if user_id.lower() == 'admin':
        admin_dashboard()
    elif user_id.startswith('SV'): # Ví dụ SV001
        student_portal(user_id)
    elif user_id.startswith('GV'): # Ví dụ GV001
        lecturer_portal(user_id)
    else:
        print("Error: Incorrect ID or password. Try again.")

# ==================================================
# 8.2. Admin dashboard
# ==================================================
def admin_dashboard():
    while True:
        print("\n[ADMIN DASHBOARD]")
        print("Welcome, System Administrator")
        print("--------------------------------------------------")
        print("1. Manage Students")
        print("2. Manage Lecturers")
        print("3. Manage Course")
        print("4. Manage Notifications")
        print("0. Logout")
        print("--------------------------------------------------")
        
        selection = input("Selection: ")
        
        if selection == '1':
            print("- Manage Students: Add, update, delete, or search student details.")
        elif selection == '2':
            print("- Manage Lecturers: Create accounts, assign departments, etc.")
        elif selection == '3':
            print("- Manage Course: Define subjects, codes, and credit hours.")
        elif selection == '4':
            print("- Manage Notifications: Draft, publish, or edit announcements.")
        elif selection == '0':
            print("- Logout: Session cleared. Returning to Main Menu.")
            break
        else:
            print("Invalid selection.")

# ==================================================
# 8.3. Student portal
# ==================================================
def student_portal(student_id):
    while True:
        print(f"\n[STUDENT PORTAL]")
        print(f"Welcome: {name} (ID: {student_id})")
        print("--------------------------------------------------")
        print("1. View Academic Transcript (Grades)")
        print("2. Check Academic Calendar")
        print("3. Register for Courses")
        print("4. Update Personal Profile")
        print("0. Logout")
        print("--------------------------------------------------")
        
        selection = input("Selection: ")
        
        if selection == '1':
            print("- View Academic Transcript: Displaying grades, credits, and cumulative GPA.")
        elif selection == '2':
            print("- Check Academic Calendar: Viewing registration periods and holidays.")
        elif selection == '3':
            print("- Register for Courses: Browse available courses or drop modules.")
        elif selection == '4':
            print("- Update Personal Profile: Modifying phone, email, or address.")
        elif selection == '0':
            print("- Logout: Ending session. Returning to Main Menu.")
            break
        else:
            print("Invalid selection.")

# ==================================================
# 8.4. Lecturer portal
# ==================================================
def lecturer_portal(user_id):
    while True:
        print(f"\n[LECTURER PORTAL]")
        print(f"Welcome: {name}")
        print("--------------------------------------------------")
        print("1. Update Student Grades")
        print("2. Search Student/Course Info")
        print("0. Logout")
        print("--------------------------------------------------")
        
        selection = input("Selection: ")
        
        if selection == '1':
            print("- Update Student Grades: Entering marks for assignments, midterms, and finals.")
        elif selection == '2':
            print("- Search Student/Course Info: Viewing enrollment lists and schedules.")
        elif selection == '0':
            print("- Logout: Ending session. Returning to Main Menu.")
            break
        else:
            print("Invalid selection.")

def view_public_notifications():
    print("\n- View Public Notifications: Displaying most recent news and school announcements.")

# Khởi chạy ứng dụng
if __name__ == "__main__":
    main_menu()
