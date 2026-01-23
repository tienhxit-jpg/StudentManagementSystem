class Course:
    def __init__(self, course_id, name, credits, prerequisite=None):
        self.course_id = course_id
        self.name = name
        self.credits = credits          # positive integer
        self.prerequisite = prerequisite  # course_id hoặc None


class Admin:
    def __init__(self):
        self.courses = {}  # key: course_id

    def add_course(self, course_id, name, credits, prerequisite=None):
        if not isinstance(credits, int) or credits <= 0:
            raise ValueError("Credits must be a positive integer")

        if course_id in self.courses:
            raise ValueError("Duplicate course ID")

        self.courses[course_id] = Course(
            course_id, name, credits, prerequisite
        )

    def update_course(self, course_id, name=None, credits=None, prerequisite=None):
        if course_id not in self.courses:
            raise ValueError("Course not found")

        course = self.courses[course_id]

        if credits is not None:
            if not isinstance(credits, int) or credits <= 0:
                raise ValueError("Credits must be a positive integer")
            course.credits = credits

        if name is not None:
            course.name = name

        if prerequisite is not None:
            course.prerequisite = prerequisite

    def delete_course(self, course_id):
        if course_id not in self.courses:
            raise ValueError("Course not found")
        del self.courses[course_id]


# Xây dựng hệ thống Quản lý thông báo cho Admin 
class Admin:
    def manage_notif(self, notifications, action, notification=None):
        if action == "create" and notification:
            notifications.append(notification)
            print("Notification created successfully.")

        elif action == "delete" and notification:
            notifications[:] = [
                n for n in notifications if n.notif_id != notification.notif_id
            ]
            print("Notification deleted successfully.")

