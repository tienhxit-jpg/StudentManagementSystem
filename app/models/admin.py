class Course:
    def __init__(self, course_id, name, credits, prerequisites=None):
        self.course_id = course_id
        self.name = name
        self.credits = credits
        self.prerequisites = prerequisites or []


class Admin:
    def __init__(self):
        self.courses = {}

    def add_course(self, course):
        self.courses[course.course_id] = course

    def update_course(self, course_id, name=None, credits=None):
        if course_id in self.courses:
            if name:
                self.courses[course_id].name = name
            if credits:
                self.courses[course_id].credits = credits

    def delete_course(self, course_id):
        if course_id in self.courses:
            del self.courses[course_id]
