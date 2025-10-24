from django.db import models
import uuid
from student_signup_signin.models import Student  # your Student model

class ClearanceDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=255)
    department_name = models.CharField(max_length=255)
    additional_notes = models.TextField(blank=True, null=True)
    file_url = models.TextField(blank=True, null=True)  # could be FileField if you want uploads
    status = models.CharField(max_length=50, default='Pending')
    time_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.first_name} - {self.document_type}"
