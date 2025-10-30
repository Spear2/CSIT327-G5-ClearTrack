import uuid
from django.db import models
from student_signup_signin.models import Student

class ClearanceDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='clearance_documents')
    document_type = models.CharField(max_length=255)
    department_name = models.CharField(max_length=255)
    additional_notes = models.TextField(blank=True, null=True)
    file_url = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Pending')
    time_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_type} - {self.student.first_name} {self.student.last_name}"
