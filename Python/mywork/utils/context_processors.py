from UserManagement.models import Notification
from student_signup_signin.models import Student
from Faculty.models import Faculty


def notification_context(request):
    user = None
    notifications = Notification.objects.none()
    unread_count = 0
    
    # faculty logged in
    if request.session.get("faculty_email"):
        try:
            faculty = Faculty.objects.get(email=request.session["faculty_email"])
            notifications = Notification.objects.filter(
                faculty_recipient=faculty
            ).order_by("-created_at")

            print("CTX DEBUG →", request.session.get("faculty_email"), notifications)
            print("DEBUG: notifications =", notifications, type(notifications))
        except Faculty.DoesNotExist:
            pass

    # student logged in
    elif request.session.get("student_email"):
        try:
            student = Student.objects.get(email_address=request.session["student_email"])
            notifications = Notification.objects.filter(
                student_recipient=student
            ).order_by("-created_at")
            print("CTX DEBUG →", request.session.get("faculty_email"), notifications)
            print("DEBUG: notifications =", notifications, type(notifications))
        except Student.DoesNotExist:
            pass

    unread_count = notifications.filter(is_read=False).count()

    return {
        "notifications": notifications,
        "unread_count": unread_count,
    }