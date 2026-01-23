import sqlite3

# Database configuration
DB_FILE = 'db_management.db'

def get_connection():
    return sqlite3.connect(DB_FILE)

def setup_database():
    """Ensure Enrollment table has all required columns"""
    conn = get_connection()
    cursor = conn.cursor()
    cols = [('process_grade','REAL'), ('final_grade','REAL'), ('grade_4_scale','REAL'), ('letter_grade','TEXT')]
    for col, dtype in cols:
        try: cursor.execute(f"ALTER TABLE Enrollment ADD COLUMN {col} {dtype} DEFAULT 0")
        except: pass
    conn.commit()
    conn.close()

def calculate_conversions(s):
    if s >= 8.5: 
        return 4.0, 'A'
    if s >= 8.0: 
        return 3.5, 'B+'
    if s >= 7.0: 
        return 3.0, 'B'
    if s >= 6.5: 
        return 2.5, 'C+'
    if s >= 5.5: 
        return 2.0, 'C'
    if s >= 5.0: 
        return 1.5, 'D+'
    if s >= 4.0: 
        return 1.0, 'D'
    return 0.0, 'F'

def get_valid_grade(prompt):
    while True:
        try:
            val = float(input(prompt))
            if 0 <= val <= 10: return val
            print("(!) Error: Grade must be between 0 and 10.")
        except ValueError:
            print("(!) Error: Please enter a valid number.")

def select_course(lecturer_id):
    """Utility to pick a course"""
    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT courseID, courseName FROM Course WHERE lecturer_id = ?", (lecturer_id,))
    courses = cursor.fetchall(); conn.close()
    if not courses: return None
    
    print("\n--- YOUR COURSES ---")
    for i, c in enumerate(courses): print(f"{i+1}. {c[0]} - {c[1]}")
    try:
        idx = int(input("Select course (number): ")) - 1
        if 0 <= idx < len(courses): return courses[idx]
    except: pass
    return None

# --- Main Feature Modules ---

def view_grades(lecturer_id):
    """Feature 1: View all student grades in a course"""
    course = select_course(lecturer_id)
    if not course: return

    conn = get_connection(); cursor = conn.cursor()
    cursor.execute('''
        SELECT u.ID, u.fullName, e.process_grade, e.final_grade, e.grade, e.grade_4_scale, e.letter_grade
        FROM Enrollment e JOIN User u ON e.student_id = u.ID WHERE e.course_id = ?
    ''', (course[0],))
    data = cursor.fetchall(); conn.close()

    print(f"\n{'='*82}")
    print(f"GRADE REPORT: {course[1]}")
    print(f"{'='*82}")
    print(f"{'ID':<10} {'Full Name':<20} {'Proc':<8} {'Final':<8} {'Total':<8} {'GPA':<8} {'Letter'}")
    print("-" * 82)
    for r in data:
        print(f"{r[0]:<10} {r[1]:<20} {r[2]:<8.1f} {r[3]:<8.1f} {r[4]:<8.1f} {r[5]:<8.1f} {r[6]:<8}")
    print(f"{'='*82}")

def input_grade(lecturer_id):
    """Feature 2: Input new grades for a student"""
    course = select_course(lecturer_id)
    if not course: return

    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT u.ID, u.fullName FROM Enrollment e JOIN User u ON e.student_id = u.ID WHERE e.course_id = ?", (course[0],))
    students = cursor.fetchall()

    print("\n--- SELECT STUDENT ---")
    for i, s in enumerate(students): print(f"{i+1}. {s[0]} - {s[1]}")
    
    try:
        idx = int(input("Select student number: ")) - 1
        sid, sname = students[idx]
        p = get_valid_grade(f"Enter Process Grade for {sname}: ")
        f = get_valid_grade(f"Enter Final Grade for {sname}: ")
        
        total = round((p * 0.3) + (f * 0.7), 2)
        s4, let = calculate_conversions(total)

        cursor.execute("UPDATE Enrollment SET process_grade=?, final_grade=?, grade=?, grade_4_scale=?, letter_grade=? WHERE student_id=? AND course_id=?", 
                       (p, f, total, s4, let, sid, course[0]))
        conn.commit(); print(f"✓ Saved: {total} ({let})")
    except: print("(!) Input failed.")
    finally: conn.close()

def edit_grade(lecturer_id):
    """Feature 3: Edit existing student grades"""
    course = select_course(lecturer_id)
    if not course: return

    conn = get_connection(); cursor = conn.cursor()
    cursor.execute("SELECT u.ID, u.fullName, e.grade FROM Enrollment e JOIN User u ON e.student_id = u.ID WHERE e.course_id = ?", (course[0],))
    students = cursor.fetchall()

    print("\n--- EDIT STUDENT GRADE ---")
    for i, s in enumerate(students): print(f"{i+1}. {s[0]} - {s[1]} (Current: {s[2]})")

    try:
        idx = int(input("Select student to edit: ")) - 1
        sid, sname = students[idx][0], students[idx][1]
        p = get_valid_grade(f"New Process Grade: ")
        f = get_valid_grade(f"New Final Grade: ")
        
        total = round((p * 0.3) + (f * 0.7), 2)
        s4, let = calculate_conversions(total)

        cursor.execute("UPDATE Enrollment SET process_grade=?, final_grade=?, grade=?, grade_4_scale=?, letter_grade=? WHERE student_id=? AND course_id=?", 
                       (p, f, total, s4, let, sid, course[0]))
        conn.commit(); print("✓ Grade updated successfully!")
    except: print("(!) Edit failed.")
    finally: conn.close()
