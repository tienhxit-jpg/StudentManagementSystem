from ..database.db_manager import DatabaseManager as DBManager

class Student:
    MAX_CREDITS = 20;

    def __init__(self, student_id, date_of_birth, major, enrollment_year, gpa=0.0):
        self.student_id = student_id  # student_id = user_id
        self.user_id = student_id  # Keep for backward compatibility
        self.date_of_birth = date_of_birth
        self.major = major
        self.enrollment_year = enrollment_year
        self.gpa = gpa
    
    # Lay ma user tuong ung voi 
    @staticmethod
    def get_by_user_id(user_id, db):
        query = "SELECT * FROM students WHERE student_id = ?"
        rows = db.execute_query(query, (user_id,))
        if rows:
            row = rows[0]
            return Student(row['student_id'], 
                           row['date_of_birth'], row['major'], row['enrollment_year'], row['gpa'])
        return None
    
    def student_menu(self):
        from .user import User
        
        db = DBManager()
        while True:
            print(f"\n[STUDENT PORTAL]")
            print(f"Welcome: {User.get_name_by_id(self.user_id, db)} (ID: {self.student_id})")
            print("--------------------------------------------------")
            print("1. View Academic Transcript (Grades)")
            print("2. Check Academic Calendar")
            print("3. Register for Courses")
            print("4. View Notifications")
            print("5. Update Personal Profile")
            print("0. Logout")
            print("--------------------------------------------------")
            
            selection = input("Selection: ")
            
            if selection == '1':
                self.view_grade()
            elif selection == '2':
                self.check_calendar()
            elif selection == '3':
                self.register_courses()
            elif selection == '4':
                self.view_notifications()
            elif selection == '5':
                print("- Update Personal Profile: Modifying phone, email, or address.")
            elif selection == '0':
                print("- Logout: Ending session. Returning to Main Menu.")
                break
            else:
                print("Invalid selection.")

    # Tinh tong so tin chi da hoan thanh
    def total_credits(self):
        from .enrollment import Enrollment
        from .course import Course
        
        db = DBManager()
        enrolled_courses = Enrollment.get_completed_courses(self.student_id, db)
        return sum(Course(course_id=course_id, name="", credits=0).credits for course_id in enrolled_courses)
    
    # Kiem tra sinh vien co the dang ky mon hoc hay khong
    def can_register(self, course):
        from .enrollment import Enrollment
        
        # Kiểm tra tín chỉ tối đa
        if self.total_credits() + course.credits > self.MAX_CREDITS:
            return False, "Exceed maximum credits"

        # Kiểm tra môn tiên quyết
        db = DBManager()
        completed_courses = Enrollment.get_completed_courses(self.student_id, db)
        if course.prerequisite and course.prerequisite not in completed_courses:
            return False, "Prerequisite not met"
        return True, ""
    
    def view_grade(self):
        """Hiển thị bảng điểm chi tiết của sinh viên theo từng học kỳ"""
        from .grade import Grade
        
        print(f"\n{'='*100}")
        print(f"[ACADEMIC TRANSCRIPT] - Student ID: {self.student_id}")
        print(f"{'='*100}")
        
        db = DBManager()
        
        # Lấy thống kê tổng quan
        stats = Grade.get_grade_statistics(self.student_id, db)
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   • Cumulative GPA: {stats['cumulative_gpa']:.2f}/4.0")
        print(f"   • Average Grade: {stats['average_grade']:.2f}/10.0")
        print(f"   • Total Courses: {stats['total_courses']} (Passed: {stats['passed_courses']}, Failed: {stats['failed_courses']})")
        print(f"   • Total Credits: {stats['total_credits']} (Passed: {stats['passed_credits']})")
        
        # Query để lấy điểm theo từng học kỳ với weight
        query = """
            SELECT s.semester, s.year, c.course_id, c.name, c.credits, 
                   e.process_grade, e.final_grade, e.grade, e.status,
                   c.process_weight, c.final_weight
            FROM enrollments e
            JOIN schedules s ON e.schedule_id = s.schedule_id
            JOIN courses c ON e.course_id = c.course_id
            WHERE e.student_id = ?
            ORDER BY s.year DESC, s.semester DESC
        """
        rows = db.execute_query(query, (self.student_id,))
        
        if not rows:
            print("\n⚠️  No grades recorded yet.")
            input("\nPress Enter to continue...")
            return
        
        # Nhóm theo học kỳ
        current_term = None
        semester_courses = []
        
        for row in rows:
            term = f"Semester {row['semester']} - Year {row['year']}"
            
            # Khi chuyển sang học kỳ mới, tính GPA học kỳ cũ
            if term != current_term:
                if current_term and semester_courses:
                    # Tính GPA cho học kỳ vừa rồi
                    prev_sem = int(current_term.split()[1])
                    prev_year = int(current_term.split()[-1])
                    semester_gpa = Grade.calculate_semester_gpa(
                        self.student_id, prev_sem, prev_year, db
                    )
                    print(f"\n   📈 Semester GPA: {semester_gpa:.2f}/4.0")
                    print(f"{'-'*100}")
                
                # Bắt đầu học kỳ mới
                current_term = term
                semester_courses = []
                print(f"\n{'='*100}")
                print(f"📚 {current_term}")
                print(f"{'='*100}")
                print(f"{'Course ID':<12} {'Course Name':<30} {'Credits':<8} {'Process':<10} {'Final':<10} {'Total':<8} {'Grade':<8} {'Status':<12}")
                print(f"{'-'*100}")
            
            # Tính điểm chữ với weight của course
            if row['grade'] is not None and row['grade'] > 0:
                # Helper function to get value from Row
                def get_row_val(r, key, default):
                    try:
                        return r[key] if key in r.keys() else default
                    except (KeyError, TypeError):
                        return default
                
                process_weight = get_row_val(row, 'process_weight', 0.3)
                final_weight = get_row_val(row, 'final_weight', 0.7)
                grade_obj = Grade(0, self.student_id, row['course_id'], 
                                 row['process_grade'], row['final_grade'],
                                 process_weight, final_weight)
                letter_grade = grade_obj.letter_grade
            else:
                letter_grade = "N/A"
            
            # Hiển thị thông tin môn học
            process = f"{row['process_grade']:.1f}" if row['process_grade'] else "N/A"
            final = f"{row['final_grade']:.1f}" if row['final_grade'] else "N/A"
            total = f"{row['grade']:.1f}" if row['grade'] else "N/A"
            
            # Định dạng status
            status_map = {
                'registered': '📝 Register',
                'completed': '✅ Pass',
                'failed': '❌ Fail',
                'dropped': '🚫 Dropped'
            }
            status_display = status_map.get(row['status'], row['status'])
            
            print(f"{row['course_id']:<12} {row['name']:<30} {row['credits']:<8} "
                  f"{process:<10} {final:<10} {total:<8} {letter_grade:<8} {status_display:<12}")
            
            semester_courses.append(row)
        
        # Tính GPA cho học kỳ cuối cùng
        if current_term and semester_courses:
            last_sem = int(current_term.split()[1])
            last_year = int(current_term.split()[-1])
            semester_gpa = Grade.calculate_semester_gpa(
                self.student_id, last_sem, last_year, db
            )
            print(f"\n   📈 Semester GPA: {semester_gpa:.2f}/4.0")
            print(f"{'-'*100}")
        
        print(f"\n{'='*100}")
        print("📌 Note: Grade weight (Process% + Final%) may vary by course.")
        print("   Check with your instructor for specific course weight configuration.")
        print("Grade Scale: A+ (9.5+), A (8.5+), B+ (8.0+), B (7.0+), C+ (6.5+), C (5.5+), D+ (5.0+), D (4.0+), F (<4.0)")
        print(f"{'='*100}")
        
        input("\nPress Enter to continue...")

    def check_calendar(self):
        from .schedule import Schedule
        
        print("\n[ACADEMIC CALENDAR] - Weekly Schedule")
        Schedule.view_schedule(self.student_id)

    def register_courses(self):
        from datetime import datetime
        from .course import Course
        
        print("\n[COURSE REGISTRATION]")
        
        db = DBManager()
        current_date = datetime.now().date()
        
        # Tự động xác định semester và year từ ngày hiện tại
        current_month = current_date.month
        year = str(current_date.year)
        
        # Logic xác định học kỳ:
        # Tháng 1-5: Học kỳ 2 (Spring)
        # Tháng 6-8: Học kỳ hè (Summer) 
        # Tháng 9-12: Học kỳ 1 (Fall)
        if 1 <= current_month <= 5:
            semester = "2"
        elif 6 <= current_month <= 8:
            semester = "3"  # Summer semester
        else:  # 9-12
            semester = "1"
        
        print(f"Registration for: Semester {semester}, Year {year}")
        print(f"Current date: {current_date}")
        
        # Get available schedules (exclude already enrolled courses in same semester)
        # Only show courses within registration period
        query = """
            SELECT s.schedule_id, s.course_id, c.name, c.credits, s.day_of_week, s.start_time, s.end_time, s.room,
                   c.register_start_date, c.register_end_date
            FROM schedules s
            JOIN courses c ON s.course_id = c.course_id
            WHERE s.semester = ? AND s.year = ?
            AND s.course_id NOT IN (
                SELECT e.course_id FROM enrollments e
                JOIN schedules sch ON e.schedule_id = sch.schedule_id
                WHERE e.student_id = ? AND sch.semester = ? AND sch.year = ?
            )
        """
        rows = db.execute_query(query, (semester, year, self.student_id, semester, year))
        
        if not rows:
            print("No available courses found or you are already enrolled.")
            return

        # Filter courses by registration period
        available_courses = []
        for row in rows:
            course = Course.get_by_id(row['course_id'], db)
            if course and course.is_registration_open(current_date):
                available_courses.append(row)
        
        if not available_courses:
            print("No courses are currently open for registration.")
            print(f"Current date: {current_date}")
            return

        print(f"\nAvailable Courses ({semester} {year}):")
        print(f"{'ID':<5} {'Course':<10} {'Name':<25} {'Credits':<8} {'Day':<10} {'Time':<12} {'Room':<8}")
        print("-" * 85)
        
        available = {str(r['schedule_id']): r for r in available_courses}
        for sid, row in available.items():
            time_str = f"{row['start_time']}-{row['end_time']}"
            print(f"{sid:<5} {row['course_id']:<10} {row['name']:<25} {row['credits']:<8} {row['day_of_week']:<10} {time_str:<12} {row['room']:<8}")

        choice = input("\nEnter Schedule ID to register (0 to cancel): ")
        if choice == '0' or choice not in available:
            if choice != '0': print("Invalid selection.")
            return

        selected = available[choice]
        
        # Double-check registration period
        course = Course.get_by_id(selected['course_id'], db)
        if not course.is_registration_open(current_date):
            print(f"Registration failed: Course is not open for registration.")
            print(f"Registration period: {course.register_start_date} to {course.register_end_date}")
            print(f"Current date: {current_date}")
            return
        
        # Check prerequisites (using a temporary object for validation)
        c_rows = db.execute_query("SELECT * FROM courses WHERE course_id = ?", (selected['course_id'],))
        if c_rows:
            c_data = c_rows[0]
            # Mock object with necessary attributes for can_register
            class CourseCheck:
                def __init__(self, credits, prerequisite):
                    self.credits = credits
                    self.prerequisite = prerequisite
            
            check_obj = CourseCheck(c_data['credits'], c_data['prerequisite'] if 'prerequisite' in c_data.keys() else None)
            allowed, msg = self.can_register(check_obj)
            if not allowed:
                print(f"Registration failed: {msg}")
                return

        # Check time conflict
        t_query = """
            SELECT s.day_of_week, s.start_time, s.end_time
            FROM enrollments e
            JOIN schedules s ON e.schedule_id = s.schedule_id
            WHERE e.student_id = ? AND s.semester = ? AND s.year = ?
        """
        enrolled = db.execute_query(t_query, (self.student_id, semester, year))
        
        s_start = self._time_to_minutes(selected['start_time'])
        s_end = self._time_to_minutes(selected['end_time'])
        
        for item in enrolled:
            if item['day_of_week'] == selected['day_of_week']:
                e_start = self._time_to_minutes(item['start_time'])
                e_end = self._time_to_minutes(item['end_time'])
                if max(s_start, e_start) < min(s_end, e_end):
                    print(f"Registration failed: Time conflict on {item['day_of_week']}.")
                    return

        # Register
        try:
            query = "INSERT INTO enrollments (student_id, course_id, schedule_id, status) VALUES (?, ?, ?, ?)"
            db.execute_query(query, (self.student_id, selected['course_id'], choice, 'registered'))
            print("Successfully registered!")
        except Exception as e:
            print(f"Database error: {e}")

    def _time_to_minutes(self, t_str):
        h, m = map(int, t_str.split(':'))
        return h * 60 + m

    def view_notifications(self):
        """View personal notifications for this student"""
        from .notification import Notification
        
        db = DBManager()
        notifications = Notification.get_user_notifications(self.user_id, db)
        
        if not notifications:
            print("\n📭 You have no notifications.")
            input("\nPress Enter to continue...")
            return
        
        # Separate unread and read notifications
        unread = [n for n in notifications if not n.is_read]
        read = [n for n in notifications if n.is_read]
        
        print(f"\n[YOUR NOTIFICATIONS]")
        print(f"Unread: {len(unread)} | Read: {len(read)} | Total: {len(notifications)}")
        print("=" * 80)
        
        # Display all notifications
        for n in notifications:
            type_icon = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'success': '✅',
                'error': '❌'
            }
            icon = type_icon.get(n.notif_type, 'ℹ️')
            read_status = "📖" if n.is_read else "🔔"
            scope = "📢" if n.is_public else "👤"
            print(f"{n.notif_id}. {read_status} {scope} {icon} {n.title}")
            print(f"   {n.date_created}")
        
        # Option to read details
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

    def update_profile(self):
        print("\n[PERSONAL PROFILE]")
        print("Feature under development.")

    def __repr__(self) -> str:
        return f"Student(ID: {self.student_id}, UserID: {self.user_id}, Major: {self.major}, Enrollment Year: {self.enrollment_year}, GPA: {self.gpa})"



    
