"""Student Management System - Main Entry Point"""
import sys
import os

# Change to parent directory so we can import app package
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.models.user import User
from app.database.db_manager import DatabaseManager

def clear_screen():
    """Clear terminal screen (cross-platform)"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print system header"""
    print("\n" + "=" * 70)
    print(" " * 15 + "STUDENT MANAGEMENT SYSTEM")
    print(" " * 20 + "Version 1.0 - Group 02")
    print("=" * 70)

def main():
    """Main program entry point"""
    try:
        db = DatabaseManager('student_management.db')
        clear_screen()
        print_header()
        
        # Create a dummy User object to access user_menu
        # The actual login happens inside user_menu()
        user = User(user_id="", password="", full_name="", email="", role="")
        user.user_menu()
        
        db.disconnect()
    except KeyboardInterrupt:
        print("\n\n⚠️  Program interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
    finally:
        print("\n" + "=" * 70)
        print(" " * 20 + "Thank you! Goodbye! 👋")
        print("=" * 70 + "\n")

if __name__ == "__main__":
    main()