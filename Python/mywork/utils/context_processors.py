from UserManagement.models import Notification
from student_signup_signin.models import Student
from Faculty.models import Faculty
from django.core.cache import cache


def notification_context(request):
    faculty_id = request.session.get("faculty_id")
    student_id = request.session.get("student_id")

    if not faculty_id and not student_id:
        return {"notifications": [], "unread_count": 0}

    user_id = faculty_id or student_id
    cache_key = f"notif_{user_id}"

    cached = cache.get(cache_key)
    if cached:
        return cached

    if faculty_id:
        qs = Notification.objects.filter(faculty_recipient_id=faculty_id)
    else:
        qs = Notification.objects.filter(student_recipient_id=student_id)

    # Use only the needed fields
    qs = qs.only("title", "message", "created_at", "is_read")

    notifications = qs.order_by("-created_at")[:30]
    unread_count = qs.filter(is_read=False).count()

    data = {
        "notifications": notifications,
        "unread_count": unread_count,
    }

    cache.set(cache_key, data, 10)
    return data