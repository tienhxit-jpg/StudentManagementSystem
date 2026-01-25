"""Schedule model"""
from ..database.db_manager import DatabaseManager as DBManager

class Schedule:
    def __init__(self, schedule_id, course_id, lecturer_id, semester,
                  year, day_of_week, start_time, end_time, room, course_name=None):
        self.schedule_id = schedule_id
        self.course_id = course_id
        self.lecturer_id = lecturer_id
        self.semester = semester
        self.year = year
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.room = room
        self.course_name = course_name

    @staticmethod
    def get_schedules_by_userID(user_id, db):
        query = """
            SELECT s.schedule_id, s.course_id, s.lecturer_id, s.semester, 
                   s.year, s.day_of_week, s.start_time, s.end_time, s.room, c.name as course_name
            FROM schedules s
            JOIN courses c ON s.course_id = c.course_id
            WHERE s.lecturer_id = ?
            UNION
            SELECT s.schedule_id, s.course_id, s.lecturer_id, s.semester, 
                   s.year, s.day_of_week, s.start_time, s.end_time, s.room, c.name as course_name
            FROM schedules s
            JOIN courses c ON s.course_id = c.course_id
            JOIN enrollments e ON s.schedule_id = e.schedule_id
            WHERE e.student_id = ?
        """
        rows = db.execute_query(query, (user_id, user_id))
        
        schedules = []
        for row in rows:
            schedules.append(Schedule(
                row['schedule_id'], row['course_id'], row['lecturer_id'],
                row['semester'], row['year'], row['day_of_week'],
                row['start_time'], row['end_time'], row['room'], row['course_name']
            ))
        return schedules

    @staticmethod
    def view_schedule(user_id):
        print("\n[ACADEMIC CALENDAR] - Weekly Schedule")
        db = DBManager()
        schedules = Schedule.get_schedules_by_userID(user_id, db)
        
        if not schedules:
            print("No schedule found.")
            return

        # Sort by year and semester to get the latest one
        schedules.sort(key=lambda x: (x.year, x.semester), reverse=True)
        current_year = schedules[0].year
        current_semester = schedules[0].semester
        
        print(f"Semester: {current_semester} {current_year}")
        print(f"{'Day':<12} {'Time':<15} {'Course':<35} {'Room':<10}")
        print("-" * 75)
        
        days_order = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 
                      'Friday': 5, 'Saturday': 6, 'Sunday': 7}
        current_schedules = [s for s in schedules if s.year == current_year and s.semester == current_semester]
        current_schedules.sort(key=lambda x: (days_order.get(x.day_of_week, 8), x.start_time))
        
        for s in current_schedules:
            time_str = f"{s.start_time}-{s.end_time}"
            course_display = f"{s.course_id} - {s.course_name}" if s.course_name else s.course_id
            print(f"{s.day_of_week:<12} {time_str:<15} {course_display:<35} {s.room:<10}")
