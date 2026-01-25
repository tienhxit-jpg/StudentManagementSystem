import hashlib
from ..database.db_manager import DatabaseManager as DBManager


class User:
    def __init__(self, user_id: str, password: str, full_name: str, email: str, role: str):
        self.user_id = user_id
        self.password = password
        self.full_name = full_name
        self.email = email
        self.role = role  # 'student', 'lecturer', 'admin'

    @staticmethod
    def hash_password(password: str) -> str:
        
        #Mã hóa mật khẩu bằng SHA-256

        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def login(user_id: str, password: str, db: DBManager):
        try:
            hashed_pass = User.hash_password(password)
            # Tim user trong database - support both username and user_id
            query = """
            SELECT user_id, full_name, email, role
            FROM users
            WHERE (username = ? OR user_id = ?) AND password = ?
            """
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute(query, (user_id, user_id, hashed_pass))
            user_data = cursor.fetchone()

            if user_data:
                user_id, full_name, email, role = user_data
                return User(user_id, hashed_pass, full_name, email, role)
            else:
                return None
        except Exception as e:
            print(f"Error during login: {e}")
            return None

# Chức năng xem thông báo công cộng cho User
    def view_notif(self, notifications):
        if not notifications:
            print("No announcements available.")
            return

        print("\n===== PUBLIC NOTIFICATIONS =====")
        for n in notifications:
            type_icon = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'success': '✅',
                'error': '❌'
            }
            icon = type_icon.get(n.notif_type, 'ℹ️')
            print(f"{n.notif_id}. {icon} {n.title}")

        choice = input("\nEnter Notification ID to read details or '0' to go back: ")

        if choice == "0":
            return

        try:
            choice_id = int(choice)
            for n in notifications:
                if n.notif_id == choice_id:
                    print(f"\n{n.get_detail()}")
                    input("\nPress Enter to continue...")
                    return
            print("Invalid Notification ID.")
        except ValueError:
            print("Please enter a valid number.")

    @staticmethod
    def get_name_by_id(user_id, db):
        query = "SELECT full_name FROM users WHERE user_id = ?"
        rows = db.execute_query(query, (user_id,))
        if rows:
            return rows[0]['full_name']
        return "Unknown User"


# Menu chính cho User
    def user_menu(self):
        while True:
            print("\n===== STUDENT MANAGEMENT SYSTEM =====")
            print("1. View Public Announcements")
            print("2. Login")
            print("0. Exit")
            print("=====================================")

            choice = input("Select an option: ")

            if choice == "1":
                from .notification import Notification
                db = DBManager()
                notifications = Notification.get_all_public_notifications(db)
                self.view_notif(notifications)
            elif choice == "2":
                user_id = input("Enter User ID: ")
                password = input("Enter Password: ")
                db = DBManager()
                user = User.login(user_id, password, db)
                if user:
                    print(f"Login successful! Welcome, {user.full_name}.")
                    # Here you can redirect to role-specific menus
                    if user.role == 'student':
                        from .student import Student
                        student = Student.get_by_user_id(user.user_id, db)
                        if student:
                            student.student_menu()
                    elif user.role == 'lecturer':
                        from .lecturer import Lecturer
                        lecturer = Lecturer.get_by_user_id(user.user_id, db)
                        if lecturer:
                            lecturer.lecturer_menu()
                    elif user.role == 'admin':
                        from .admin import Admin
                        admin = Admin.get_by_user_id(user.user_id, db)
                        if admin:
                            admin.admin_menu()
                else:
                    print("Login failed! Invalid User ID or Password.")
            elif choice == "0":
                print("Exiting the system. Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")