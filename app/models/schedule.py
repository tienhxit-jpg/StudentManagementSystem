import sqlite3

# Database configuration
DB_FILE = 'db_management.db'

def get_connection():
    return sqlite3.connect(DB_FILE)

def view_schedule(lecturer_id):
    """
    Use-case 11: Check Timetable
    Retrieves and displays the teaching schedule for the lecturer.
    """
    print("\n" + "="*70)
    print(f"{'MY TEACHING SCHEDULE':^70}")
    print("="*70)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Join Course and Schedule based on the Class Diagram (input_file_3)
        # Retrieves Course ID, Name, Time, and Location
        cursor.execute('''
            SELECT c.courseID, c.courseName, s.time, s.location
            FROM Course c
            JOIN Schedule s ON c.courseID = s.courseID
            WHERE c.lecturerID = ?
            ORDER BY s.time ASC
        ''', (lecturer_id,))
        
        timetable = cursor.fetchall()

        # Alternative Flow: If no timetable data is found
        if not timetable:
            print("(!) Notification: No timetable available for your assigned courses.")
        else:
            # Main Flow: Display the timetable
            print(f"{'Course ID':<12} {'Course Name':<25} {'Time':<20} {'Location':<10}")
            print("-" * 70)
            
            for row in timetable:
                print(f"{row[0]:<12} {row[1]:<25} {row[2]:<20} {row[3]:<10}")
            
            print("-" * 70)
            print(f"Total sessions found: {len(timetable)}")

    except Exception as e:
        print(f"(!) Error retrieving timetable: {e}")
    finally:
        conn.close()

def view_student_schedule(student_id):
    """
    Use-case 11: Check Timetable (Student Version)
    Retrieves the schedule for courses the student is enrolled in.
    """
    print("\n" + "="*75)
    print(f"{'MY PERSONAL STUDY SCHEDULE':^75}")
    print("="*75)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Logic: Enrollment -> Course -> Schedule
        # We find courses where studentID matches, then get their schedule details
        cursor.execute('''
            SELECT c.courseID, c.courseName, s.time, s.location
            FROM Enrollment e
            JOIN Course c ON e.courseID = c.courseID
            JOIN Schedule s ON c.courseID = s.courseID
            WHERE e.studentID = ?
            ORDER BY s.time ASC
        ''', (student_id,))
        
        timetable = cursor.fetchall()

        # Alternative flow: If no enrolled courses or no schedule found
        if not timetable:
            print("(!) Notification: You are not enrolled in any courses with a scheduled time.")
        else:
            # Main flow: Display the timetable
            print(f"{'Course ID':<12} {'Course Name':<28} {'Time':<20} {'Room':<10}")
            print("-" * 75)
            
            for row in timetable:
                print(f"{row[0]:<12} {row[1]:<28} {row[2]:<20} {row[3]:<10}")
            
            print("-" * 75)
            print(f"Total class sessions: {len(timetable)}")

    except Exception as e:
        print(f"(!) Error: Could not retrieve your timetable. {e}")
    finally:
        conn.close()
