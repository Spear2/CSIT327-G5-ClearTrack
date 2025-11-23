from UserManagement.models import Notification
from student_signup_signin.models import Student
from Faculty.models import Faculty

def notify_faculty(faculty, title, message):
    Notification.objects.create(
        faculty_recipient=faculty,
        title=title,
        message=message
    )

def notify_student(student, title, message):
    Notification.objects.create(
        student_recipient=student,
        title=title,
        message=message
    )

