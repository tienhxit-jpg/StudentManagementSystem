class Admin:
    def __init__(self, db=None):
        self.db = db
    
    def admin_menu(self):
        while True:
            print("\n[ADMIN DASHBOARD]")
            print("Welcome, System Administrator")
            print("--------------------------------------------------")
            print("1. Manage Students")
            print("2. Manage Lecturers")
            print("3. Manage Courses")
            print("4. Manage Notifications")
            print("0. Logout")
            print("--------------------------------------------------")
            
            selection = input("Selection: ")
            
            if selection == '1':
                self.manage_student()
            elif selection == '2':
                self.manage_lecturer()
            elif selection == '3':
                self.manage_course()
            elif selection == '4':
                self.manage_notification()
            elif selection == '0':
                break
            else:
                print("Invalid selection.")

    @staticmethod
    def get_by_user_id(user_id, db):
        query = "SELECT * FROM admins WHERE admin_id = ?"
        rows = db.execute_query(query, (user_id,))
        if rows:
            row = rows[0]
            return Admin(db)
        return None
    
    def manage_student(self):
        while True:
            print("\n[MANAGE STUDENTS]")
            print("1. View All Students")
            print("2. Add Student")
            print("3. Update Student")
            print("4. Delete Student")
            print("0. Back")
            print("--------------------------------------------------")
            
            selection = input("Selection: ")
            
            if selection == '1':
                self.view_students_paginated()
            elif selection == '2':
                self.add_student()
            elif selection == '3':
                self.update_student()
            elif selection == '4':
                self.delete_student()
            elif selection == '0':
                break
            else:
                print("Invalid selection.")

    def view_students(self, page=1, per_page=10):
        """
        Xem danh sách sinh viên với phân trang
        
        Args:
            page: Số trang hiện tại (bắt đầu từ 1)
            per_page: Số sinh viên trên mỗi trang
        """
        print(f"\n[VIEW ALL STUDENTS - Page {page}]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return 0, 0
        
        try:
            # Đếm tổng số sinh viên
            count_query = "SELECT COUNT(*) as total FROM students"
            count_result = self.db.execute_query(count_query)
            total_students = count_result[0]['total'] if count_result else 0
            
            if total_students == 0:
                print("No students found.")
                return 0, 0
            
            # Tính toán phân trang
            total_pages = (total_students + per_page - 1) // per_page  # Ceiling division
            
            # Validate page number
            if page < 1:
                page = 1
            elif page > total_pages:
                page = total_pages
            
            offset = (page - 1) * per_page
            
            # JOIN với bảng users để lấy thông tin đầy đủ với LIMIT và OFFSET
            query = """
                SELECT 
                    s.student_id,
                    u.full_name,
                    u.email,
                    u.phone,
                    s.major,
                    s.enrollment_year,
                    s.gpa,
                    s.date_of_birth
                FROM students s
                JOIN users u ON s.user_id = u.user_id
                ORDER BY s.student_id
                LIMIT ? OFFSET ?
            """
            
            rows = self.db.execute_query(query, (per_page, offset))
            
            if not rows:
                print("No students found on this page.")
                return total_students, total_pages
            
            # Header với format đẹp
            print(f"\n{'No.':<5} {'Student ID':<12} {'Full Name':<22} {'Major':<18} {'Year':<6} {'GPA':<6} {'Email':<28}")
            print("-" * 110)
            
            # Hiển thị từng sinh viên (số thứ tự global, không reset mỗi page)
            start_idx = offset + 1
            for idx, row in enumerate(rows, start_idx):
                student_id = row['student_id']
                full_name = row['full_name'][:21] if row['full_name'] else 'N/A'
                email = row['email'][:27] if row['email'] else 'N/A'
                major = row['major'][:17] if row['major'] else 'N/A'
                year = row['enrollment_year'] if row['enrollment_year'] else 'N/A'
                gpa = f"{row['gpa']:.2f}" if row['gpa'] is not None else 'N/A'
                
                print(f"{idx:<5} {student_id:<12} {full_name:<22} {major:<18} {year:<6} {gpa:<6} {email:<28}")
            
            # Footer với thông tin phân trang
            print("-" * 110)
            print(f"Showing {start_idx}-{start_idx + len(rows) - 1} of {total_students} student(s) | Page {page}/{total_pages}")
            print("=" * 110)
            
            return total_students, total_pages
            
        except Exception as e:
            print(f"❌ Error retrieving students: {str(e)}")
            return 0, 0
    
    def view_students_paginated(self):
        """Interactive phân trang cho view students"""
        page = 1
        per_page = 10
        
        while True:
            total_students, total_pages = self.view_students(page=page, per_page=per_page)
            
            if total_students == 0:
                input("\nPress Enter to continue...")
                break
            
            # Menu điều hướng
            print("\nNavigation: [N]ext | [P]revious | [G]oto page | [C]hange page size | [B]ack")
            choice = input("Your choice: ").strip().upper()
            
            if choice == 'N':
                if page < total_pages:
                    page += 1
                else:
                    print("⚠️  Already at the last page.")
            elif choice == 'P':
                if page > 1:
                    page -= 1
                else:
                    print("⚠️  Already at the first page.")
            elif choice == 'G':
                try:
                    goto_page = int(input(f"Enter page number (1-{total_pages}): "))
                    if 1 <= goto_page <= total_pages:
                        page = goto_page
                    else:
                        print(f"⚠️  Invalid page number. Must be between 1 and {total_pages}.")
                except ValueError:
                    print("⚠️  Invalid input. Please enter a number.")
            elif choice == 'C':
                try:
                    new_size = int(input("Enter items per page (5-50): "))
                    if 5 <= new_size <= 50:
                        per_page = new_size
                        page = 1  # Reset to first page
                    else:
                        print("⚠️  Invalid size. Must be between 5 and 50.")
                except ValueError:
                    print("⚠️  Invalid input. Please enter a number.")
            elif choice == 'B':
                break
            else:
                print("⚠️  Invalid choice.")

    def add_student(self):
        """Thêm sinh viên mới"""
        print("\n[ADD NEW STUDENT]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        try:
            # Nhập thông tin user
            print("\n--- User Information ---")
            student_id = input("Student ID (e.g., S001, will be used as User ID): ").strip()
            if not student_id:
                print("❌ Student ID cannot be empty.")
                return
            
            user_id = student_id  # student_id = user_id
            
            # Kiểm tra user_id đã tồn tại chưa
            check_query = "SELECT user_id FROM users WHERE user_id = ?"
            existing = self.db.execute_query(check_query, (user_id,))
            if existing:
                print(f"❌ Student ID {student_id} already exists.")
                return
            
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            full_name = input("Full Name: ").strip()
            email = input("Email: ").strip()
            phone = input("Phone: ").strip()
            
            # Nhập thông tin student
            print("\n--- Student Information ---")
            date_of_birth = input("Date of Birth (YYYY-MM-DD): ").strip()
            major = input("Major: ").strip()
            enrollment_year = input("Enrollment Year (e.g., 2024): ").strip()
            gpa = input("GPA (0.0-4.0, default 0.0): ").strip()
            gpa = float(gpa) if gpa else 0.0
            
            # Validate
            if not all([username, password, full_name, email, major, enrollment_year]):
                print("❌ All required fields must be filled.")
                return
            
            # Insert vào database
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (user_id, username, password, role, full_name, email, phone)
                VALUES (?, ?, ?, 'student', ?, ?, ?)
            """, (user_id, username, password, full_name, email, phone))
            
            # Insert student (student_id = user_id, no separate user_id column)
            cursor.execute("""
                INSERT INTO students (student_id, date_of_birth, major, enrollment_year, gpa)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, date_of_birth, major, int(enrollment_year), gpa))
            
            conn.commit()
            
            print("\n" + "=" * 110)
            print(f"✅ Student {student_id} ({full_name}) added successfully!")
            print("=" * 110)
            
        except ValueError as e:
            print(f"❌ Invalid input: {str(e)}")
        except Exception as e:
            print(f"❌ Error adding student: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()

    def update_student(self):
        """Cập nhật thông tin sinh viên"""
        print("\n[UPDATE STUDENT]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        # Tìm sinh viên
        student_id = input("Enter Student ID to update: ").strip()
        if not student_id:
            print("❌ Student ID cannot be empty.")
            return
        
        # Lấy thông tin hiện tại
        query = """
            SELECT s.*, u.full_name, u.email, u.phone, u.username
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.student_id = ?
        """
        rows = self.db.execute_query(query, (student_id,))
        
        if not rows:
            print(f"❌ Student ID {student_id} not found.")
            return
        
        student = rows[0]
        
        # Hiển thị thông tin hiện tại
        print(f"\n--- Current Information for {student_id} ---")
        print(f"Name: {student['full_name']}")
        print(f"Email: {student['email']}")
        print(f"Phone: {student['phone']}")
        print(f"Major: {student['major']}")
        print(f"Enrollment Year: {student['enrollment_year']}")
        print(f"GPA: {student['gpa']}")
        print(f"Date of Birth: {student['date_of_birth']}")
        
        # Menu cập nhật
        print("\n--- What to update? ---")
        print("1. Full Name")
        print("2. Email")
        print("3. Phone")
        print("4. Major")
        print("5. GPA")
        print("6. Date of Birth")
        print("0. Cancel")
        
        choice = input("\nYour choice: ").strip()
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            if choice == '1':
                new_value = input("Enter new Full Name: ").strip()
                if new_value:
                    cursor.execute("UPDATE users SET full_name = ? WHERE user_id = ?", 
                                 (new_value, student['user_id']))
                    print(f"✅ Full Name updated to: {new_value}")
            
            elif choice == '2':
                new_value = input("Enter new Email: ").strip()
                if new_value:
                    cursor.execute("UPDATE users SET email = ? WHERE user_id = ?", 
                                 (new_value, student['user_id']))
                    print(f"✅ Email updated to: {new_value}")
            
            elif choice == '3':
                new_value = input("Enter new Phone: ").strip()
                if new_value:
                    cursor.execute("UPDATE users SET phone = ? WHERE user_id = ?", 
                                 (new_value, student['user_id']))
                    print(f"✅ Phone updated to: {new_value}")
            
            elif choice == '4':
                new_value = input("Enter new Major: ").strip()
                if new_value:
                    cursor.execute("UPDATE students SET major = ? WHERE student_id = ?", 
                                 (new_value, student_id))
                    print(f"✅ Major updated to: {new_value}")
            
            elif choice == '5':
                new_value = input("Enter new GPA (0.0-4.0): ").strip()
                if new_value:
                    gpa = float(new_value)
                    if 0.0 <= gpa <= 4.0:
                        cursor.execute("UPDATE students SET gpa = ? WHERE student_id = ?", 
                                     (gpa, student_id))
                        print(f"✅ GPA updated to: {gpa}")
                    else:
                        print("❌ GPA must be between 0.0 and 4.0")
                        return
            
            elif choice == '6':
                new_value = input("Enter new Date of Birth (YYYY-MM-DD): ").strip()
                if new_value:
                    cursor.execute("UPDATE students SET date_of_birth = ? WHERE student_id = ?", 
                                 (new_value, student_id))
                    print(f"✅ Date of Birth updated to: {new_value}")
            
            elif choice == '0':
                print("Update cancelled.")
                return
            
            else:
                print("❌ Invalid choice.")
                return
            
            conn.commit()
            
        except ValueError as e:
            print(f"❌ Invalid input: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()
        except Exception as e:
            print(f"❌ Error updating student: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()

    def delete_student(self):
        """Xóa sinh viên"""
        print("\n[DELETE STUDENT]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        # Tìm sinh viên
        student_id = input("Enter Student ID to delete: ").strip()
        if not student_id:
            print("❌ Student ID cannot be empty.")
            return
        
        # Lấy thông tin sinh viên
        query = """
            SELECT s.*, u.full_name
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.student_id = ?
        """
        rows = self.db.execute_query(query, (student_id,))
        
        if not rows:
            print(f"❌ Student ID {student_id} not found.")
            return
        
        student = rows[0]
        
        # Xác nhận xóa
        print(f"\n⚠️  You are about to delete:")
        print(f"   Student ID: {student_id}")
        print(f"   Name: {student['full_name']}")
        print(f"   Major: {student['major']}")
        
        confirm = input("\nAre you sure? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("Delete cancelled.")
            return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Xóa student (user sẽ tự động xóa do CASCADE)
            cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            cursor.execute("DELETE FROM users WHERE user_id = ?", (student['user_id'],))
            
            conn.commit()
            
            print(f"\n✅ Student {student_id} deleted successfully!")
            
        except Exception as e:
            print(f"❌ Error deleting student: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()
    
    def manage_lecturer(self):
        """Quản lý giảng viên"""
        while True:
            print("\n[MANAGE LECTURERS]")
            print("1. View All Lecturers")
            print("2. Add Lecturer")
            print("3. Update Lecturer")
            print("4. Delete Lecturer")
            print("0. Back")
            print("--------------------------------------------------")
            
            selection = input("Selection: ")
            
            if selection == '1':
                self.view_lecturers()
            elif selection == '2':
                self.add_lecturer()
            elif selection == '3':
                self.update_lecturer()
            elif selection == '4':
                self.delete_lecturer()
            elif selection == '0':
                break
            else:
                print("Invalid selection.")
    
    def view_lecturers(self):
        """Xem danh sách giảng viên"""
        print("\n[VIEW ALL LECTURERS]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        query = """
            SELECT 
                l.lecturer_id,
                u.full_name,
                u.email,
                u.phone,
                l.department,
                l.specialization,
                l.hire_date
            FROM lecturers l
            JOIN users u ON l.user_id = u.user_id
            ORDER BY l.lecturer_id
        """
        
        try:
            rows = self.db.execute_query(query)
            
            if not rows:
                print("No lecturers found.")
                return
            
            print(f"\n{'No.':<5} {'Lecturer ID':<12} {'Full Name':<25} {'Department':<20} {'Email':<30}")
            print("-" * 110)
            
            for idx, row in enumerate(rows, 1):
                lecturer_id = row['lecturer_id']
                full_name = row['full_name'][:24] if row['full_name'] else 'N/A'
                email = row['email'][:29] if row['email'] else 'N/A'
                dept = row['department'][:19] if row['department'] else 'N/A'
                
                print(f"{idx:<5} {lecturer_id:<12} {full_name:<25} {dept:<20} {email:<30}")
            
            print("-" * 110)
            print(f"Total: {len(rows)} lecturer(s)")
            print("=" * 110)
            
        except Exception as e:
            print(f"❌ Error retrieving lecturers: {str(e)}")
    
    def add_lecturer(self):
        """Thêm giảng viên mới"""
        print("\n[ADD NEW LECTURER]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        try:
            # Nhập thông tin user
            print("\n--- User Information ---")
            lecturer_id = input("Lecturer ID (e.g., L001, will be used as User ID): ").strip()
            if not lecturer_id:
                print("❌ Lecturer ID cannot be empty.")
                return
            
            user_id = lecturer_id  # lecturer_id = user_id
            
            # Kiểm tra user_id đã tồn tại chưa
            check_query = "SELECT user_id FROM users WHERE user_id = ?"
            existing = self.db.execute_query(check_query, (user_id,))
            if existing:
                print(f"❌ Lecturer ID {lecturer_id} already exists.")
                return
            
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            full_name = input("Full Name: ").strip()
            email = input("Email: ").strip()
            phone = input("Phone: ").strip()
            
            # Nhập thông tin lecturer
            print("\n--- Lecturer Information ---")
            department = input("Department: ").strip()
            
            # Validate
            if not all([username, password, full_name, email, department]):
                print("❌ Required fields must be filled.")
                return
            
            # Insert vào database
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (user_id, username, password, role, full_name, email, phone)
                VALUES (?, ?, ?, 'lecturer', ?, ?, ?)
            """, (user_id, username, password, full_name, email, phone))
            
            # Insert lecturer (lecturer_id = user_id, no separate user_id column)
            cursor.execute("""
                INSERT INTO lecturers (lecturer_id, department)
                VALUES (?, ?)
            """, (lecturer_id, department))
            
            conn.commit()
            
            print("\n" + "=" * 110)
            print(f"✅ Lecturer {lecturer_id} ({full_name}) added successfully!")
            print("=" * 110)
            
        except ValueError as e:
            print(f"❌ Invalid input: {str(e)}")
        except Exception as e:
            print(f"❌ Error adding lecturer: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()
    
    def update_lecturer(self):
        """Cập nhật thông tin giảng viên"""
        print("\n[UPDATE LECTURER]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        # Tìm giảng viên
        lecturer_id = input("Enter Lecturer ID to update: ").strip()
        if not lecturer_id:
            print("❌ Lecturer ID cannot be empty.")
            return
        
        # Lấy thông tin hiện tại
        query = """
            SELECT l.*, u.full_name, u.email, u.phone, u.username
            FROM lecturers l
            JOIN users u ON l.user_id = u.user_id
            WHERE l.lecturer_id = ?
        """
        rows = self.db.execute_query(query, (lecturer_id,))
        
        if not rows:
            print(f"❌ Lecturer ID {lecturer_id} not found.")
            return
        
        lecturer = rows[0]
        
        # Hiển thị thông tin hiện tại
        print(f"\n--- Current Information for {lecturer_id} ---")
        print(f"Name: {lecturer['full_name']}")
        print(f"Email: {lecturer['email']}")
        print(f"Phone: {lecturer['phone']}")
        print(f"Department: {lecturer['department']}")
        print(f"Specialization: {lecturer['specialization']}")
        print(f"Hire Date: {lecturer['hire_date']}")
        
        # Menu cập nhật
        print("\n--- What to update? ---")
        print("1. Full Name")
        print("2. Email")
        print("3. Phone")
        print("4. Department")
        print("5. Specialization")
        print("6. Hire Date")
        print("0. Cancel")
        
        choice = input("\nYour choice: ").strip()
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            if choice == '1':
                new_value = input("Enter new Full Name: ").strip()
                if new_value:
                    cursor.execute("UPDATE users SET full_name = ? WHERE user_id = ?", 
                                 (new_value, lecturer['user_id']))
                    print(f"✅ Full Name updated to: {new_value}")
            
            elif choice == '2':
                new_value = input("Enter new Email: ").strip()
                if new_value:
                    cursor.execute("UPDATE users SET email = ? WHERE user_id = ?", 
                                 (new_value, lecturer['user_id']))
                    print(f"✅ Email updated to: {new_value}")
            
            elif choice == '3':
                new_value = input("Enter new Phone: ").strip()
                if new_value:
                    cursor.execute("UPDATE users SET phone = ? WHERE user_id = ?", 
                                 (new_value, lecturer['user_id']))
                    print(f"✅ Phone updated to: {new_value}")
            
            elif choice == '4':
                new_value = input("Enter new Department: ").strip()
                if new_value:
                    cursor.execute("UPDATE lecturers SET department = ? WHERE lecturer_id = ?", 
                                 (new_value, lecturer_id))
                    print(f"✅ Department updated to: {new_value}")
            
            elif choice == '5':
                new_value = input("Enter new Specialization: ").strip()
                if new_value:
                    cursor.execute("UPDATE lecturers SET specialization = ? WHERE lecturer_id = ?", 
                                 (new_value, lecturer_id))
                    print(f"✅ Specialization updated to: {new_value}")
            
            elif choice == '6':
                new_value = input("Enter new Hire Date (YYYY-MM-DD): ").strip()
                if new_value:
                    cursor.execute("UPDATE lecturers SET hire_date = ? WHERE lecturer_id = ?", 
                                 (new_value, lecturer_id))
                    print(f"✅ Hire Date updated to: {new_value}")
            
            elif choice == '0':
                print("Update cancelled.")
                return
            
            else:
                print("❌ Invalid choice.")
                return
            
            conn.commit()
            
        except ValueError as e:
            print(f"❌ Invalid input: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()
        except Exception as e:
            print(f"❌ Error updating lecturer: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()
    
    def delete_lecturer(self):
        """Xóa giảng viên"""
        print("\n[DELETE LECTURER]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        # Tìm giảng viên
        lecturer_id = input("Enter Lecturer ID to delete: ").strip()
        if not lecturer_id:
            print("❌ Lecturer ID cannot be empty.")
            return
        
        # Lấy thông tin giảng viên
        query = """
            SELECT l.*, u.full_name
            FROM lecturers l
            JOIN users u ON l.user_id = u.user_id
            WHERE l.lecturer_id = ?
        """
        rows = self.db.execute_query(query, (lecturer_id,))
        
        if not rows:
            print(f"❌ Lecturer ID {lecturer_id} not found.")
            return
        
        lecturer = rows[0]
        
        # Xác nhận xóa
        print(f"\n⚠️  You are about to delete:")
        print(f"   Lecturer ID: {lecturer_id}")
        print(f"   Name: {lecturer['full_name']}")
        print(f"   Department: {lecturer['department']}")
        
        confirm = input("\nAre you sure? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("Delete cancelled.")
            return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Xóa lecturer (user sẽ tự động xóa do CASCADE)
            cursor.execute("DELETE FROM lecturers WHERE lecturer_id = ?", (lecturer_id,))
            cursor.execute("DELETE FROM users WHERE user_id = ?", (lecturer['user_id'],))
            
            conn.commit()
            
            print(f"\n✅ Lecturer {lecturer_id} deleted successfully!")
            
        except Exception as e:
            print(f"❌ Error deleting lecturer: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()
    
    def manage_course(self):
        """Quản lý khóa học"""
        while True:
            print("\n[MANAGE COURSES]")
            print("1. View All Courses")
            print("2. Add Course")
            print("3. Update Course")
            print("4. Delete Course")
            print("0. Back")
            print("--------------------------------------------------")
            
            selection = input("Selection: ")
            
            if selection == '1':
                self.view_courses()
            elif selection == '2':
                self.add_course()
            elif selection == '3':
                self.update_course()
            elif selection == '4':
                self.delete_course()
            elif selection == '0':
                break
            else:
                print("Invalid selection.")
    
    def view_courses(self):
        """Xem danh sách khóa học"""
        print("\n[VIEW ALL COURSES]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        query = """
            SELECT 
                course_id,
                name,
                credits,
                prerequisite,
                description,
                max_students
            FROM courses
            ORDER BY course_id
        """
        
        try:
            rows = self.db.execute_query(query)
            
            if not rows:
                print("No courses found.")
                return
            
            print(f"\n{'No.':<5} {'Course ID':<12} {'Name':<35} {'Credits':<8} {'Prerequisite':<15}")
            print("-" * 110)
            
            for idx, row in enumerate(rows, 1):
                course_id = row['course_id']
                name = row['name'][:34] if row['name'] else 'N/A'
                credits = row['credits']
                prereq = row['prerequisite'] if row['prerequisite'] else 'None'
                
                print(f"{idx:<5} {course_id:<12} {name:<35} {credits:<8} {prereq:<15}")
            
            print("-" * 110)
            print(f"Total: {len(rows)} course(s)")
            print("=" * 110)
            
        except Exception as e:
            print(f"❌ Error retrieving courses: {str(e)}")
    
    def add_course(self):
        """Thêm khóa học mới"""
        print("\n[ADD NEW COURSE]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        try:
            course_id = input("Course ID (e.g., CS101): ").strip()
            if not course_id:
                print("❌ Course ID cannot be empty.")
                return
            
            # Kiểm tra course_id đã tồn tại chưa
            check_query = "SELECT course_id FROM courses WHERE course_id = ?"
            existing = self.db.execute_query(check_query, (course_id,))
            if existing:
                print(f"❌ Course ID {course_id} already exists.")
                return
            
            name = input("Course Name: ").strip()
            credits = input("Credits: ").strip()
            prerequisite = input("Prerequisite (leave empty if none): ").strip()
            description = input("Description: ").strip()
            max_students = input("Max Students (default 50): ").strip()
            
            # Nhập hệ số điểm
            print("\n--- Grade Weight Configuration ---")
            print("Process weight + Final weight must equal 1.0 (100%)")
            print("Examples: 0.3 + 0.7, 0.4 + 0.6, 0.5 + 0.5")
            
            process_weight_input = input("Process Grade Weight (default 0.3 = 30%): ").strip()
            if process_weight_input:
                process_weight = float(process_weight_input)
                if not (0 <= process_weight <= 1):
                    print("❌ Process weight must be between 0 and 1.")
                    return
            else:
                process_weight = 0.3
            
            final_weight_input = input(f"Final Grade Weight (default {1 - process_weight:.1f} = {int((1 - process_weight) * 100)}%): ").strip()
            if final_weight_input:
                final_weight = float(final_weight_input)
                if not (0 <= final_weight <= 1):
                    print("❌ Final weight must be between 0 and 1.")
                    return
            else:
                final_weight = 1 - process_weight
            
            # Kiểm tra tổng = 1.0
            if abs(process_weight + final_weight - 1.0) > 0.001:
                print(f"❌ Process weight ({process_weight}) + Final weight ({final_weight}) must equal 1.0")
                return
            
            # Nhập thời gian đăng ký
            print("\n--- Registration Period ---")
            register_start_date = input("Registration Start Date (YYYY-MM-DD, leave empty if none): ").strip()
            register_end_date = input("Registration End Date (YYYY-MM-DD, leave empty if none): ").strip()
            
            # Validate dates if provided
            if register_start_date or register_end_date:
                from datetime import datetime
                try:
                    if register_start_date:
                        datetime.strptime(register_start_date, '%Y-%m-%d')
                    if register_end_date:
                        datetime.strptime(register_end_date, '%Y-%m-%d')
                    
                    # Check if both dates provided and start < end
                    if register_start_date and register_end_date:
                        if register_start_date >= register_end_date:
                            print("❌ End date must be after start date.")
                            return
                except ValueError:
                    print("❌ Invalid date format. Use YYYY-MM-DD.")
                    return
            
            register_start_date = register_start_date if register_start_date else None
            register_end_date = register_end_date if register_end_date else None
            
            if not all([name, credits]):
                print("❌ Name and Credits are required.")
                return
            
            max_students = int(max_students) if max_students else 50
            prerequisite = prerequisite if prerequisite else None
            
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO courses (course_id, name, credits, prerequisite, description, max_students,
                                   process_weight, final_weight, register_start_date, register_end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (course_id, name, int(credits), prerequisite, description, max_students,
                  process_weight, final_weight, register_start_date, register_end_date))
            
            conn.commit()
            
            print(f"\n✅ Course {course_id} ({name}) added successfully!")
            print(f"   Grade Formula: Process ({int(process_weight * 100)}%) + Final ({int(final_weight * 100)}%) = Total")
            if register_start_date and register_end_date:
                print(f"   Registration Period: {register_start_date} to {register_end_date}")
            else:
                print(f"   Registration Period: Not set")
            
        except ValueError as e:
            print(f"❌ Invalid input: {str(e)}")
        except Exception as e:
            print(f"❌ Error adding course: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()
    
    def update_course(self):
        """Cập nhật khóa học"""
        print("\n[UPDATE COURSE]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        # Tìm khóa học
        course_id = input("Enter Course ID to update: ").strip()
        if not course_id:
            print("❌ Course ID cannot be empty.")
            return
        
        # Lấy thông tin hiện tại
        query = "SELECT * FROM courses WHERE course_id = ?"
        rows = self.db.execute_query(query, (course_id,))
        
        if not rows:
            print(f"❌ Course ID {course_id} not found.")
            return
        
        course = rows[0]
        
        # Hiển thị thông tin hiện tại
        print(f"\n--- Current Information for {course_id} ---")
        print(f"Name: {course['name']}")
        print(f"Credits: {course['credits']}")
        print(f"Prerequisite: {course['prerequisite'] if course['prerequisite'] else 'None'}")
        print(f"Description: {course['description']}")
        print(f"Max Students: {course['max_students']}")
        
        # Hiển thị weight nếu có
        process_weight = course.get('process_weight', 0.3)
        final_weight = course.get('final_weight', 0.7)
        print(f"Grade Formula: Process ({int(process_weight * 100)}%) + Final ({int(final_weight * 100)}%) = Total")
        
        # Hiển thị registration dates
        register_start = course.get('register_start_date', None)
        register_end = course.get('register_end_date', None)
        if register_start and register_end:
            print(f"Registration Period: {register_start} to {register_end}")
        else:
            print(f"Registration Period: Not set")
        
        # Menu cập nhật
        print("\n--- What to update? ---")
        print("1. Course Name")
        print("2. Credits")
        print("3. Prerequisite")
        print("4. Description")
        print("5. Max Students")
        print("6. Grade Weight Configuration")
        print("7. Registration Period")
        print("0. Cancel")
        
        choice = input("\nYour choice: ").strip()
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            if choice == '1':
                new_value = input("Enter new Course Name: ").strip()
                if new_value:
                    cursor.execute("UPDATE courses SET name = ? WHERE course_id = ?", 
                                 (new_value, course_id))
                    print(f"✅ Course Name updated to: {new_value}")
            
            elif choice == '2':
                new_value = input("Enter new Credits: ").strip()
                if new_value:
                    credits = int(new_value)
                    if credits > 0:
                        cursor.execute("UPDATE courses SET credits = ? WHERE course_id = ?", 
                                     (credits, course_id))
                        print(f"✅ Credits updated to: {credits}")
                    else:
                        print("❌ Credits must be positive")
                        return
            
            elif choice == '3':
                new_value = input("Enter new Prerequisite (leave empty for none): ").strip()
                cursor.execute("UPDATE courses SET prerequisite = ? WHERE course_id = ?", 
                             (new_value if new_value else None, course_id))
                print(f"✅ Prerequisite updated to: {new_value if new_value else 'None'}")
            
            elif choice == '4':
                new_value = input("Enter new Description: ").strip()
                if new_value:
                    cursor.execute("UPDATE courses SET description = ? WHERE course_id = ?", 
                                 (new_value, course_id))
                    print(f"✅ Description updated")
            
            elif choice == '5':
                new_value = input("Enter new Max Students: ").strip()
                if new_value:
                    max_students = int(new_value)
                    if max_students > 0:
                        cursor.execute("UPDATE courses SET max_students = ? WHERE course_id = ?", 
                                     (max_students, course_id))
                        print(f"✅ Max Students updated to: {max_students}")
                    else:
                        print("❌ Max Students must be positive")
                        return
            
            elif choice == '6':
                print("\n--- Update Grade Weight Configuration ---")
                print("Process weight + Final weight must equal 1.0 (100%)")
                current_process = course.get('process_weight', 0.3)
                current_final = course.get('final_weight', 0.7)
                print(f"Current: Process {int(current_process * 100)}% + Final {int(current_final * 100)}%")
                
                process_weight_input = input(f"New Process Grade Weight (current {current_process}): ").strip()
                if process_weight_input:
                    process_weight = float(process_weight_input)
                    if not (0 <= process_weight <= 1):
                        print("❌ Process weight must be between 0 and 1.")
                        return
                    
                    final_weight = 1 - process_weight
                    print(f"Final weight will be set to: {final_weight:.2f}")
                    
                    # Kiểm tra tổng = 1.0
                    if abs(process_weight + final_weight - 1.0) > 0.001:
                        print(f"❌ Invalid weights (sum = {process_weight + final_weight})")
                        return
                    
                    cursor.execute("""
                        UPDATE courses 
                        SET process_weight = ?, final_weight = ? 
                        WHERE course_id = ?
                    """, (process_weight, final_weight, course_id))
                    
                    print(f"✅ Grade weights updated!")
                    print(f"   New Formula: Process ({int(process_weight * 100)}%) + Final ({int(final_weight * 100)}%) = Total")
                else:
                    print("❌ No changes made")
                    return
            
            elif choice == '7':
                print("\n--- Update Registration Period ---")
                current_start = course.get('register_start_date', None)
                current_end = course.get('register_end_date', None)
                print(f"Current: {current_start} to {current_end}" if current_start and current_end else "Current: Not set")
                
                register_start_date = input("New Start Date (YYYY-MM-DD, leave empty to keep current): ").strip()
                register_end_date = input("New End Date (YYYY-MM-DD, leave empty to keep current): ").strip()
                
                # Validate dates if provided
                from datetime import datetime
                try:
                    if register_start_date:
                        datetime.strptime(register_start_date, '%Y-%m-%d')
                    else:
                        register_start_date = current_start
                    
                    if register_end_date:
                        datetime.strptime(register_end_date, '%Y-%m-%d')
                    else:
                        register_end_date = current_end
                    
                    # Check if both dates provided and start < end
                    if register_start_date and register_end_date:
                        if register_start_date >= register_end_date:
                            print("❌ End date must be after start date.")
                            return
                    
                    cursor.execute("""
                        UPDATE courses 
                        SET register_start_date = ?, register_end_date = ? 
                        WHERE course_id = ?
                    """, (register_start_date, register_end_date, course_id))
                    
                    print(f"✅ Registration period updated!")
                    if register_start_date and register_end_date:
                        print(f"   Period: {register_start_date} to {register_end_date}")
                    else:
                        print(f"   Period: Not set")
                    
                except ValueError:
                    print("❌ Invalid date format. Use YYYY-MM-DD.")
                    return
            
            elif choice == '0':
                print("Update cancelled.")
                return
            
            else:
                print("❌ Invalid choice.")
                return
            
            conn.commit()
            
        except ValueError as e:
            print(f"❌ Invalid input: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()
        except Exception as e:
            print(f"❌ Error updating course: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()
    
    def delete_course(self):
        """Xóa khóa học"""
        print("\n[DELETE COURSE]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        # Tìm khóa học
        course_id = input("Enter Course ID to delete: ").strip()
        if not course_id:
            print("❌ Course ID cannot be empty.")
            return
        
        # Lấy thông tin khóa học
        query = "SELECT * FROM courses WHERE course_id = ?"
        rows = self.db.execute_query(query, (course_id,))
        
        if not rows:
            print(f"❌ Course ID {course_id} not found.")
            return
        
        course = rows[0]
        
        # Kiểm tra xem có khóa học nào phụ thuộc vào course này không
        check_query = "SELECT course_id, name FROM courses WHERE prerequisite = ?"
        dependent_courses = self.db.execute_query(check_query, (course_id,))
        
        if dependent_courses:
            print(f"\n⚠️  Warning: This course is a prerequisite for:")
            for dep_course in dependent_courses:
                print(f"   - {dep_course['course_id']}: {dep_course['name']}")
            print("\nYou may need to update those courses first.")
        
        # Xác nhận xóa
        print(f"\n⚠️  You are about to delete:")
        print(f"   Course ID: {course_id}")
        print(f"   Name: {course['name']}")
        print(f"   Credits: {course['credits']}")
        
        confirm = input("\nAre you sure? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("Delete cancelled.")
            return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Xóa course (schedules và enrollments sẽ tự động xóa do CASCADE)
            cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
            
            conn.commit()
            
            print(f"\n✅ Course {course_id} deleted successfully!")
            
        except Exception as e:
            print(f"❌ Error deleting course: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()

    def manage_notification(self):
        """Quản lý thông báo"""
        while True:
            print("\n[MANAGE NOTIFICATIONS]")
            print("1. View All Notifications")
            print("2. Send Notification")
            print("3. Delete Notification")
            print("0. Back")
            print("--------------------------------------------------")
            
            selection = input("Selection: ")
            
            if selection == '1':
                self.view_notifications()
            elif selection == '2':
                self.send_notification()
            elif selection == '3':
                self.delete_notification()
            elif selection == '0':
                break
            else:
                print("Invalid selection.")
    
    def view_notifications(self):
        """Xem danh sách thông báo"""
        print("\n[VIEW ALL NOTIFICATIONS]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        query = """
            SELECT 
                n.notification_id,
                n.title,
                n.message,
                n.type,
                n.is_public,
                u.full_name as recipient,
                u.role as user_role,
                n.created_at,
                n.is_read
            FROM notifications n
            LEFT JOIN users u ON n.user_id = u.user_id
            ORDER BY n.created_at DESC
            LIMIT 50
        """
        
        try:
            rows = self.db.execute_query(query)
            
            if not rows:
                print("No notifications found.")
                return
            
            print(f"\n{'ID':<6} {'Title':<30} {'Recipient':<25} {'Type':<10} {'Scope':<10}")
            print("-" * 110)
            
            for row in rows:
                notif_id = row['notification_id']
                title = row['title'][:29] if row['title'] else 'N/A'
                is_public = row['is_public']
                
                if is_public:
                    recipient = '📢 PUBLIC'
                    scope = 'All Users'
                else:
                    recipient = row['recipient'][:24] if row['recipient'] else 'N/A'
                    role = row['user_role'] if row['user_role'] else 'N/A'
                    scope = role.title()
                
                notif_type = row['type']
                
                print(f"{notif_id:<6} {title:<30} {recipient:<25} {notif_type:<10} {scope:<10}")
            
            print("-" * 110)
            print(f"Total: {len(rows)} notification(s) (showing latest 50)")
            print("=" * 110)
            
        except Exception as e:
            print(f"❌ Error retrieving notifications: {str(e)}")
    
    def send_notification(self):
        """Gửi thông báo mới"""
        print("\n[SEND NOTIFICATION]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        try:
            title = input("Notification Title: ").strip()
            if not title:
                print("❌ Title cannot be empty.")
                return
            
            message = input("Message: ").strip()
            if not message:
                print("❌ Message cannot be empty.")
                return
            
            print("\n--- Notification Type ---")
            print("1. Info")
            print("2. Warning")
            print("3. Success")
            print("4. Error")
            
            type_choice = input("\nSelect type (1-4): ").strip()
            
            type_map = {
                '1': 'info',
                '2': 'warning',
                '3': 'success',
                '4': 'error'
            }
            
            if type_choice not in type_map:
                print("❌ Invalid choice.")
                return
            
            notif_type = type_map[type_choice]
            
            print("\n--- Target Audience ---")
            print("1. 📢 Public Announcement (single notification for all)")
            print("2. All users (individual notifications)")
            print("3. Students only")
            print("4. Lecturers only")
            print("5. Admins only")
            print("6. Specific user")
            
            target_choice = input("\nSelect target (1-6): ").strip()
            
            conn = self.db.connect()
            cursor = conn.cursor()
            
            if target_choice == '1':
                # Public notification - một thông báo cho tất cả
                cursor.execute("""
                    INSERT INTO notifications (user_id, title, message, type, is_public, is_read)
                    VALUES (NULL, ?, ?, ?, 1, 0)
                """, (title, message, notif_type))
                
                print(f"\n✅ Public announcement created!")
                print(f"   This notification will be visible to ALL users.")
                
            elif target_choice == '6':
                # Gửi đến user cụ thể
                user_id = input("Enter User ID: ").strip()
                check_query = "SELECT user_id FROM users WHERE user_id = ?"
                existing = self.db.execute_query(check_query, (user_id,))
                if not existing:
                    print(f"❌ User ID {user_id} not found.")
                    return
                
                cursor.execute("""
                    INSERT INTO notifications (user_id, title, message, type, is_public, is_read)
                    VALUES (?, ?, ?, ?, 0, 0)
                """, (user_id, title, message, notif_type))
                
                print(f"\n✅ Notification sent to user {user_id}!")
                
            elif target_choice in ['2', '3', '4', '5']:
                # Gửi đến nhóm users
                role_map = {
                    '2': None,  # All
                    '3': 'student',
                    '4': 'lecturer',
                    '5': 'admin'
                }
                
                target_role = role_map[target_choice]
                
                # Lấy danh sách users theo role
                if target_role:
                    user_query = "SELECT user_id FROM users WHERE role = ?"
                    users = self.db.execute_query(user_query, (target_role,))
                else:
                    user_query = "SELECT user_id FROM users"
                    users = self.db.execute_query(user_query)
                
                if not users:
                    print("❌ No users found for this target.")
                    return
                
                # Insert notification cho từng user
                for user in users:
                    cursor.execute("""
                        INSERT INTO notifications (user_id, title, message, type, is_public, is_read)
                        VALUES (?, ?, ?, ?, 0, 0)
                    """, (user['user_id'], title, message, notif_type))
                
                print(f"\n✅ Notification sent to {len(users)} user(s)!")
                print(f"   Target: {target_role if target_role else 'All users'}")
            else:
                print("❌ Invalid choice.")
                return
            
            conn.commit()
            
            print("\n" + "=" * 110)
            print(f"✅ Notification sent successfully!")
            print(f"   Title: {title}")
            print(f"   Type: {notif_type}")
            print("=" * 110)
            
        except Exception as e:
            print(f"❌ Error sending notification: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()
    
    def delete_notification(self):
        """Xóa thông báo"""
        print("\n[DELETE NOTIFICATION]")
        print("=" * 110)
        
        if self.db is None:
            print("❌ Database connection not available.")
            return
        
        try:
            notif_id = input("Enter Notification ID to delete: ").strip()
            if not notif_id:
                print("❌ Notification ID cannot be empty.")
                return
            
            # Lấy thông tin notification
            query = "SELECT * FROM notifications WHERE notification_id = ?"
            rows = self.db.execute_query(query, (int(notif_id),))
            
            if not rows:
                print(f"❌ Notification ID {notif_id} not found.")
                return
            
            notif = rows[0]
            
            print(f"\n⚠️  You are about to delete:")
            print(f"   ID: {notif['notification_id']}")
            print(f"   Title: {notif['title']}")
            print(f"   Created: {notif['created_at']}")
            
            confirm = input("\nAre you sure? (yes/no): ").strip().lower()
            
            if confirm != 'yes':
                print("Delete cancelled.")
                return
            
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM notifications WHERE notification_id = ?", (int(notif_id),))
            
            conn.commit()
            
            print(f"\n✅ Notification {notif_id} deleted successfully!")
            
        except ValueError:
            print("❌ Invalid Notification ID. Must be a number.")
        except Exception as e:
            print(f"❌ Error deleting notification: {str(e)}")
            if self.db.connection:
                self.db.connection.rollback()