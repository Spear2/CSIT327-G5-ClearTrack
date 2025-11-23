from django.db import models

from student_signup_signin.models import Student
from Faculty.models import Faculty

class SystemAdmin(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.email
    

class Notification(models.Model):
    # Notification can belong to a faculty OR a student
    faculty_recipient = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, null=True, blank=True
    )

    student_recipient = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=True, blank=True
    )

    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.faculty_recipient.email if self.faculty_recipient else self.student_recipient.email_address
        return f"{self.title} → {target}"