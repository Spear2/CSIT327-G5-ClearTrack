from UserManagement.models import Notification
from student_signup_signin.models import Student
from Faculty.models import Faculty
from django.core.cache import cache


def notification_context(request):
    faculty_id = request.session.get("faculty_id")
    student_id = request.session.get("student_id")

    # If no user logged in → skip all queries
    if not faculty_id and not student_id:
        return {"notifications": [], "unread_count": 0}

    # Cache key per user
    cache_key = f"notif_{faculty_id or student_id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    # Build base queryset (NO SLICING HERE)
    if faculty_id:
        qs = Notification.objects.filter(faculty_recipient_id=faculty_id)
    else:
        qs = Notification.objects.filter(student_recipient_id=student_id)

    # ORDER + FILTER FIRST (ok)
    qs = qs.order_by("-created_at")

    # UNREAD COUNT (separate query)
    unread_count = qs.filter(is_read=False).count()

    # Slice LAST so no filtering happens after slicing
    notifications = qs[:30]

    result = {
        "notifications": notifications,
        "unread_count": unread_count,
    }

    # Cache for 10 seconds to prevent DB spam
    cache.set(cache_key, result, 10)

    return result
