import hashlib
from ..database.db_manager import DBManager

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
    
    """
    User passwords shall be stored in encrypted or hashed form.
    After 5 consecutive failed login attempts, the system shall temporarily block the
    account
    """
    @staticmethod
    def login(user_id: str, password: str, db: DBManager):
        try:
            hashed_pass = User.hash_password(password)
            # Tim user trong database
            query = """
            SELECT user_id, full_name, email, role
            FROM users
            WHERE user_id = ? AND password = ?
            """
            result = db.execute_query(query, (user_id, hashed_pass))
            
            if not result:
                return None  # Đăng nhập thất bại
            row = result[0]
            print(f"✓ User {row['full_name']} logged in successfully as {row['role']}.")
            return User(row['user_id'], hashed_pass, row['full_name'], row['email'], row['role'])
        except Exception as e:
            print(f"(!) Error during login: {e}")
            return None


# Chức năng xem thông báo công cộng cho User
class User:
    def view_notif(self, notifications):
        if not notifications:
            print("No announcements available.")
            return

        print("===== PUBLIC NOTIFICATIONS =====")
        for n in notifications:
            print(f"{n.notif_id}. {n.title}")

        choice = input("Enter Notification ID to read details or '0' to go back: ")

        if choice == "0":
            return

        for n in notifications:
            if n.notif_id == choice:
                print(n.get_detail())
                return

        print("Invalid Notification ID.")
