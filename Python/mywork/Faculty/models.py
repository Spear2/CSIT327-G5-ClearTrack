from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone

class Faculty(models.Model):
    DEPARTMENT_CHOICES = [
        ('Library', 'Librarian'),
        ('Registrar', 'Registrar'),
        ('Finance Office', 'Finance Office'),
        ('Guidance Office', 'Guidance Office'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(message="Enter a valid school email address.")]
    )
    password = models.CharField(max_length=255)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.department})"
    
class Comment(models.Model):
    document = models.ForeignKey(
        'studentDashboard.ClearanceDocument',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    faculty = models.ForeignKey(
        'Faculty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.faculty} on {self.document}"
    

class DepartmentSettings(models.Model):
    department = models.OneToOneField(Faculty, on_delete=models.CASCADE, related_name='settings')
    office_hours = models.TextField(blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    notify_new_submissions = models.BooleanField(default=False)
    urgent_alerts = models.BooleanField(default=False)
    daily_summary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.department.department_name} Settings"