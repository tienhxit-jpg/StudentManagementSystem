from ..database.db_manager import DatabaseManager as DBManager

class Lecturer:
    def __init__(self, lecturer_id, department, db=None):
        self.lecturer_id = lecturer_id
        self.user_id = lecturer_id  # lecturer_id = user_id
        self.department = department
        self.db = db if db is not None else DBManager()

    def lecturer_menu(self):
        """Main menu for lecturer portal"""
        # Lazy import to avoid circular dependency
        from .user import User
        
        db = DBManager()
        # Get lecturer name from database
        while True:
            print(f"\n[LECTURER PORTAL]")
            print(f"Welcome: {User.get_name_by_id(self.user_id, db)} (ID: {self.lecturer_id})")
            print("--------------------------------------------------")
            print("1. Update Student Grades")
            print("2. Check Academic Calendar")
            print("3. View Notifications")
            print("0. Logout")
            print("--------------------------------------------------")
            selection = input("Selection: ")
            if selection == '1':
                self.update_grades()
            elif selection == '2':
                self.check_calendar()
            elif selection == '3':
                self.view_notifications()
            elif selection == '0':
                print("- Logout: Ending session. Returning to Main Menu.")
                break
            else:
                print("Invalid selection.")

    def update_grades(self):
        """
        Grade Management System - Complete Workflow
        Allows instructor to manage student grades for their courses
        """
        print("\n" + "="*110)
        print("[GRADE MANAGEMENT SYSTEM]")
        print("="*110)
        
        db = DBManager()
        
        # STEP 1-2: Display courses taught by this lecturer
        print("\n[YOUR COURSES]")
        courses_query = """
            SELECT DISTINCT c.course_id, c.name, c.credits,
                   COUNT(DISTINCT e.student_id) as enrolled_count
            FROM courses c
            LEFT JOIN schedules sch ON c.course_id = sch.course_id
            LEFT JOIN enrollments e ON sch.schedule_id = e.schedule_id
            WHERE sch.lecturer_id = ?
            GROUP BY c.course_id, c.name, c.credits
            ORDER BY c.course_id
        """
        
        courses = db.execute_query(courses_query, (self.lecturer_id,))
        
        if not courses:
            print("❌ You are not assigned to any courses.")
            return
        
        print(f"\n{'No.':<5} {'Course ID':<12} {'Course Name':<40} {'Credits':<8} {'Students':<10}")
        print("-" * 110)
        for idx, course in enumerate(courses, 1):
            print(f"{idx:<5} {course['course_id']:<12} {course['name']:<40} {course['credits']:<8} {course['enrolled_count']:<10}")
        print("-" * 110)
        print(f"Total: {len(courses)} course(s)")
        
        # STEP 3: Select a course
        while True:
            course_choice = input("\nEnter course number to manage grades (or '0' to cancel): ").strip()
            
            if course_choice == '0':
                print("Cancelled.")
                return
            
            try:
                course_idx = int(course_choice) - 1
                if 0 <= course_idx < len(courses):
                    selected_course = courses[course_idx]
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(courses)}.")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
        
        course_id = selected_course['course_id']
        course_name = selected_course['name']
        
        # Get current semester and year
        import datetime
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        
        # Determine semester based on month (1-6: Spring, 7-12: Fall)
        semester = "Spring" if current_month <= 6 else "Fall"
        year = current_year
        
        print(f"\nManaging grades for: {semester} {year}")
        
        # STEP 4: Display enrolled students
        while True:
            print("\n" + "="*110)
            print(f"[COURSE: {course_id} - {course_name}]")
            print("="*110)
            
            students_query = """
                SELECT 
                    s.student_id,
                    u.user_id,
                    u.full_name,
                    s.major,
                    e.process_grade,
                    e.final_grade,
                    e.grade as overall_grade,
                    e.enrollment_id
                FROM enrollments e
                JOIN students s ON e.student_id = s.student_id
                JOIN users u ON s.student_id = u.user_id
                WHERE e.course_id = ? AND e.semester = ? AND e.year = ?
            """
            students = db.execute_query(students_query, (course_id, semester, year))
            
            # Display students table
            print(f"\n{'No.':<5} {'Student ID':<12} {'Full Name':<25} {'Major':<20} {'Process':<9} {'Final':<9} {'Overall':<9}")
            print("-" * 110)
            
            for idx, student in enumerate(students, 1):
                process = f"{student['process_grade']:.1f}" if student['process_grade'] is not None else "N/A"
                final = f"{student['final_grade']:.1f}" if student['final_grade'] is not None else "N/A"
                overall = f"{student['overall_grade']:.2f}" if student['overall_grade'] is not None else "N/A"
                
                print(f"{idx:<5} {student['student_id']:<12} {student['full_name']:<25} {student['major']:<20} {process:<9} {final:<9} {overall:<9}")
            
            print("-" * 110)
            print(f"Total: {len(students)} student(s) enrolled")
            
            # STEP 5: Search or select student
            print("\n[OPTIONS]")
            print("1. Update grades for a student")
            print("2. Search for a student")
            print("0. Back to course list")
            
            option = input("\nSelect option: ").strip()
            
            if option == '0':
                break
            elif option == '2':
                # Search functionality
                search_term = input("Enter student name or ID to search: ").strip().lower()
                filtered = [s for s in students if search_term in s['full_name'].lower() or search_term in s['student_id'].lower()]
                
                if not filtered:
                    print(f"❌ No students found matching '{search_term}'")
                    continue
                
                print(f"\n[SEARCH RESULTS: {len(filtered)} match(es)]")
                print(f"{'No.':<5} {'Student ID':<12} {'Full Name':<25} {'Process':<9} {'Final':<9} {'Overall':<9}")
                print("-" * 110)
                for idx, student in enumerate(filtered, 1):
                    process = f"{student['process_grade']:.1f}" if student['process_grade'] is not None else "N/A"
                    final = f"{student['final_grade']:.1f}" if student['final_grade'] is not None else "N/A"
                    overall = f"{student['overall_grade']:.2f}" if student['overall_grade'] is not None else "N/A"
                    print(f"{idx:<5} {student['student_id']:<12} {student['full_name']:<25} {process:<9} {final:<9} {overall:<9}")
                print("-" * 110)
                
                input("\nPress Enter to continue...")
                continue
                
            elif option == '1':
                # STEP 6: Select student to update
                student_input = input("\nEnter student number or Student ID: ").strip()
                
                selected_student = None
                
                # Check if input is a number (index)
                try:
                    student_idx = int(student_input) - 1
                    if 0 <= student_idx < len(students):
                        selected_student = students[student_idx]
                except ValueError:
                    # Input is student ID
                    for s in students:
                        if s['student_id'] == student_input:
                            selected_student = s
                            break
                
                if not selected_student:
                    print("❌ Student not found.")
                    continue
                
                # STEP 7: Enter grades for each component
                from .grade import Grade
                from .course import Course
                
                # Lấy thông tin course để biết weight
                course = Course.get_by_id(course_id, db)
                process_weight = course.process_weight if course else 0.3
                final_weight = course.final_weight if course else 0.7
                
                print("\n" + "="*110)
                print(f"[UPDATE GRADES FOR: {selected_student['full_name']} ({selected_student['student_id']})]")
                print("="*110)
                print(f"Current Grades:")
                print(f"  Process Grade: {selected_student['process_grade'] if selected_student['process_grade'] is not None else 'N/A'}")
                print(f"  Final Grade: {selected_student['final_grade'] if selected_student['final_grade'] is not None else 'N/A'}")
                print(f"  Overall Grade: {selected_student['overall_grade'] if selected_student['overall_grade'] is not None else 'N/A'}")
                print("-" * 110)
                print(f"Grade Formula: Total = Process ({int(process_weight * 100)}%) + Final ({int(final_weight * 100)}%)")
                print("Passing Grade: 4.0/10.0")
                print("-" * 110)
                
                try:
                    # Input process grade
                    process_input = input("Enter Process Grade (0-10) [press Enter to keep current]: ").strip()
                    if process_input:
                        process_grade = float(process_input)
                        if not (0 <= process_grade <= 10):
                            print("❌ Process grade must be between 0 and 10.")
                            continue
                    else:
                        process_grade = selected_student['process_grade']
                        if process_grade is None:
                            print("❌ Process grade is required.")
                            continue
                    
                    # Input final grade
                    final_input = input("Enter Final Grade (0-10) [press Enter to keep current]: ").strip()
                    if final_input:
                        final_grade = float(final_input)
                        if not (0 <= final_grade <= 10):
                            print("❌ Final grade must be between 0 and 10.")
                            continue
                    else:
                        final_grade = selected_student['final_grade']
                        if final_grade is None:
                            print("❌ Final grade is required.")
                            continue
                    
                    # STEP 8: Calculate overall grade using Grade model
                    grade_obj = Grade(
                        selected_student['enrollment_id'],
                        selected_student['student_id'],
                        course_id,
                        process_grade,
                        final_grade,
                        process_weight,
                        final_weight
                    )
                    
                    # Display calculated results
                    print("\n[CALCULATED GRADES]")
                    print(f"  Process Grade ({int(grade_obj.process_weight * 100)}%): {grade_obj.process_grade:.1f}")
                    print(f"  Final Grade ({int(grade_obj.final_weight * 100)}%): {grade_obj.final_grade:.1f}")
                    print(f"  Total Grade: {grade_obj.total_grade:.2f}/10.0")
                    print(f"  Letter Grade: {grade_obj.letter_grade}")
                    print(f"  Grade Point: {grade_obj.grade_point:.1f}/4.0")
                    print(f"  Status: {'✅ PASS' if grade_obj.is_passed() else '❌ FAIL'}")
                    
                    # STEP 9: Save option
                    print("\n" + "-" * 110)
                    confirm = input("Save these grades? (Y/N): ").strip().upper()
                    
                    if confirm != 'Y':
                        print("❌ Grades not saved.")
                        continue
                    
                    # STEP 10-11: Validate and save using Grade model
                    success = Grade.update_grade(
                        selected_student['enrollment_id'],
                        process_grade,
                        final_grade,
                        db
                    )
                    
                    if success:
                        # Send notification to student
                        notification_title = f"Grade Updated: {course_id}"
                        notification_message = (
                            f"Your grades for {course_name} have been updated.\n"
                            f"Process: {grade_obj.process_grade:.1f}, Final: {grade_obj.final_grade:.1f}\n"
                            f"Total: {grade_obj.total_grade:.2f} ({grade_obj.letter_grade})\n"
                            f"Grade Point: {grade_obj.grade_point:.1f}/4.0"
                        )
                        
                        conn = db.connect()
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO notifications (user_id, title, message, type, is_read)
                            VALUES (?, ?, ?, 'info', 0)
                        """, (selected_student['user_id'], notification_title, notification_message))
                        conn.commit()
                        
                        # STEP 12: Success message
                        print("\n" + "="*110)
                        print("✅ GRADES SAVED SUCCESSFULLY!")
                        print(f"   Student: {selected_student['full_name']} ({selected_student['student_id']})")
                        print(f"   Course: {course_name} ({course_id})")
                        print(f"   Total Grade: {grade_obj.total_grade:.2f}/10.0 ({grade_obj.letter_grade})")
                        print(f"   Grade Point: {grade_obj.grade_point:.1f}/4.0")
                        print(f"   Status: {'✅ PASS' if grade_obj.is_passed() else '❌ FAIL'}")
                        print(f"   📧 Notification sent to student")
                        print("="*110)
                    else:
                        print("❌ Error saving grades. Please try again.")
                    
                    input("\nPress Enter to continue...")
                    
                except ValueError:
                    print("❌ Invalid input. Grades must be numeric values.")
                    continue
                except Exception as e:
                    print(f"❌ Error saving grades: {str(e)}")
                    if db.connection:
                        db.connection.rollback()
                    continue
            else:
                print("❌ Invalid option.")

    def check_calendar(self):
        from .schedule import Schedule
        
        print("\n[ACADEMIC CALENDAR] - Weekly Schedule")
        db = DBManager()
        Schedule.view_schedule(self.user_id)

    def view_notifications(self):
        """View personal notifications for this lecturer"""
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
            print(f"{n.notif_id}. {read_status} {icon} {n.title}")
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


    @staticmethod
    def get_by_user_id(user_id, db):
        """Get lecturer object by user_id"""
        query = "SELECT * FROM lecturers WHERE lecturer_id = ?"
        rows = db.execute_query(query, (user_id,))
        if rows:
            row = rows[0]
            return Lecturer(row['lecturer_id'], 
                            row['department'], db)
        return None
    
    
    