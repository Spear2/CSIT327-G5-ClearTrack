from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q, Case, When, Value, IntegerField, Count
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from functools import lru_cache

from studentDashboard.models import ClearanceDocument
from student_signup_signin.models import Student
from UserManagement.models import Notification
from Faculty.models import Faculty, Comment, DepartmentSettings
from utils.notifications import notify_student  # convert this to Celery async if needed

from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

DEPARTMENT_MAP = {
    "Library": "Library",
    "Registrar": "Registrar",
    "Accounting": "Accounting",
    "Academic Adviser": "Academic Adviser",
}

@lru_cache(maxsize=1)
def get_department_map():
    return DEPARTMENT_MAP

# Create your views here.
def home(request):
    return render(request, 'LandingPage.html')


def update_status(request, document_id):

    if request.method == 'POST':

        document = get_object_or_404(ClearanceDocument, id=document_id)
        new_status = request.POST.get('status')

        # Get faculty from session
        faculty_id = request.session.get('faculty_id')
        faculty = Faculty.objects.get(id=faculty_id)

        # Normalize department names
        faculty_department = DEPARTMENT_MAP.get(faculty.department, "").lower()
        document_department = document.department_name.lower()

        # Get student correctly
        student = document.student

        # Check if faculty belongs to this department
        if faculty_department == document_department:

            document.status = new_status
            document.save()

            # Notify student
            if new_status == "Approved":
                notify_student(
                    student,
                    title="Clearance Approved",
                    message=f"Your clearance for {document.document_type} has been approved."
                )

            elif new_status == "Rejected":
                notify_student(
                    student,
                    title="Clearance Rejected",
                    message=f"Your clearance for {document.document_type} has been rejected."
                )

    return redirect('homepage')


def get_clearance_counts():

    return ClearanceDocument.objects.aggregate(
        pending=Count('id', filter=Q(status='Pending')),
        approved=Count('id', filter=Q(status='Approved')),
        rejected=Count('id', filter=Q(status='Rejected')),
    )


def filter_clearance_requests(qs, status, department, query, date_filter):


    filters = Q()

    if status != "All":
        filters &= Q(status=status)

    if department != "All_Department":
        filters &= Q(department_name=department)

    if query:
        filters &= (
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(student__student_id__icontains=query)
        )

    if date_filter != "All_Time":
        now = timezone.now()

        if date_filter == "Last_7_Days":
            filters &= Q(time_submitted__gte=now - timedelta(days=7))
        elif date_filter == "Last_30_Days":
            filters &= Q(time_submitted__gte=now - timedelta(days=30))
        elif date_filter == "This_Semester":
            month = now.month
            start_month = 6 if month >= 6 else 11
            sem_start = timezone.datetime(
                now.year,
                start_month,
                1,
                tzinfo=timezone.get_current_timezone(),
            )
            filters &= Q(time_submitted__gte=sem_start)

    return qs.filter(filters)


def annotate_and_order_requests(qs):
    return qs.annotate(
        status_priority=Case(
            When(status='Pending', then=Value(0)),
            When(status='Approved', then=Value(1)),
            When(status='Rejected', then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        )
    ).order_by("status_priority", "-time_submitted")


def get_faculty_info(request):

    faculty_id = request.session.get("faculty_id")
    if not faculty_id:
        return None, "", ""

    faculty = Faculty.objects.filter(id=faculty_id).only(
    ).first()

    if not faculty:
        return None, "", ""

    initials = (faculty.first_name[0] + faculty.last_name[0]).upper()
    faculty_department = get_department_map().get(faculty.department, "").lower()

    return faculty, initials, faculty_department


def homepage(request):
    if not request.session.get("faculty_id"):
        return redirect("faculty_signin")

    faculty, initials, faculty_department = get_faculty_info(request)

    status = request.GET.get('status', 'All')
    department = request.GET.get('department', 'All_Department')
    search = request.GET.get('search', '')
    date_filter = request.GET.get('date_filter', 'All_Time')

    # OPTIMIZED: fetch only fields used and join student efficiently
    qs = ClearanceDocument.objects.select_related("student").only(
        "status", "department_name", "time_submitted",
        "student__first_name", "student__last_name", "student__student_id"
    )

    qs = filter_clearance_requests(qs, status, department, search, date_filter)
    qs = annotate_and_order_requests(qs)

    counts = get_clearance_counts()

    context = {
        "faculty": faculty,
        "initials": initials,
        "requests": qs,
        "faculty_department": faculty_department,
        "selected_status": status,
        "selected_department": department,
        "selected_date": date_filter,
        "count_Approved": counts["approved"],
        "count_Reject": counts["rejected"],
        "count_Pending": counts["pending"],
        "SUPABASE_URL": settings.SUPABASE_URL,
        "SUPABASE_BUCKET": settings.SUPABASE_BUCKET,
    }

    return render(request, "Hompage.html", context)


def get_logged_in_faculty(request):
    faculty_id = request.session.get("faculty_id")
    if not faculty_id:
        return None
    try:
        return Faculty.objects.only("id", "first_name", "last_name", "email", "password").get(id=faculty_id)
    except Faculty.DoesNotExist:
        return None

def faculty_security(request):
    faculty = get_logged_in_faculty(request)
    if not faculty:
        return redirect('faculty_signin')

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not check_password(current_password, faculty.password):
            messages.error(request, "Current password is incorrect.")
        elif new_password != confirm_password:
            messages.error(request, "New password and confirmation do not match.")
        else:
            faculty.password = make_password(new_password)
            faculty.save()
            messages.success(request, "Password updated successfully!")

    return render(request, "Faculty_Profile.html", {"faculty": faculty, "section": "security"})


def faculty_profile(request):
    faculty = get_logged_in_faculty(request)
    if not faculty:
        return redirect('faculty_signin')

    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            try:
                validate_email(email)
                faculty.email = email
                faculty.save()
                messages.success(request, "Profile updated successfully!")
            except ValidationError:
                messages.error(request, "Enter a valid email address.")

    return render(request, "Faculty_Profile.html", {"faculty": faculty, "section": "profile"})

def department_settings(request):

    if not request.session.get('faculty_email') or not request.session.get('faculty_id'):
        return redirect('faculty_signin')
    
    faculty_id = request.session.get("faculty_id")
    faculty = Faculty.objects.get(id=faculty_id)
    settings, created = DepartmentSettings.objects.get_or_create(department=faculty)

    if request.method == 'POST':
        settings.office_hours = request.POST.get('office_hours')
        settings.special_instructions = request.POST.get('special_instructions')
        settings.contact_email = request.POST.get('contact_email')
        settings.phone_number = request.POST.get('phone_number')
        settings.notify_new_submissions = 'notify_new' in request.POST
        # settings.urgent_alerts = 'urgent_alerts' in request.POST
        # settings.daily_summary = 'daily_summary' in request.POST
        settings.save()
        return redirect('department_settings')

    return render(request, 'Faculty/department_settings.html', {'faculty': faculty, 'settings': settings})


def faculty_signin(request):

    if( request.session.get('faculty_email') and request.session.get('faculty_id')):
        return redirect('homepage')
    
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")

        # Empty field validation
        if not email or not password:
            messages.error(request, "Please fill in both email and password.")
            return render(request, "FacultySignIn.html")

        # Check if user exists
        try:
            faculty = Faculty.objects.get(email=email)
        except Faculty.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, "FacultySignIn.html")

        # Password check
        if not check_password(password, faculty.password):
            messages.error(request, "Invalid email or password.")
            return render(request, "FacultySignIn.html")

        # Session persistence (manually)
        request.session["faculty_id"] = faculty.id
        request.session["faculty_name"] = f"{faculty.first_name} {faculty.last_name}"
        request.session["faculty_email"] = faculty.email
        request.session.set_expiry(0)  # session ends on browser close

        messages.success(request, f"Welcome, {faculty.first_name}!")
        return redirect("homepage")

    return render(request, "FacultySignIn.html")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("forgot_username")

        if not email:
            messages.error(request, "Please fill in email.");
            return render(request, "ForgotPassword/FacultyForgotPassword.html")
        
        try:
            faculty = Faculty.objects.get(email=email)
        except Faculty.DoesNotExist:
            messages.error(request, "Email does not exist.")
            return render(request, "ForgotPassword/FacultyForgotPassword.html")

        request.session["forgot_email"] = faculty.email
        return redirect("new_password")
    return render(request, "ForgotPassword/FacultyForgotPassword.html")

def new_password(request):
    email = request.session.get("forgot_email")
    faculty = Faculty.objects.get(email=email)

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not new_password or not confirm_password:
            messages.error(request, "Please fill both fields");
            return render(request, "ForgotPassword/NewPassword.html", {"faculty": faculty})

        if new_password != confirm_password:
            messages.error(request, "Passwords does not match")
            return render(request, "ForgotPassword/NewPassword.html", {"faculty": faculty})
        
        faculty.password = make_password(new_password)
        faculty.save()

        messages.success(request, "Password successfully changed.")
        return redirect("faculty_signin")

    return render(request, "ForgotPassword/NewPassword.html", {"faculty": faculty})

def faculty_signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        department = request.POST.get("department")

        # Field validation
        if not all([first_name, last_name, email, password, confirm_password, department]):
            messages.error(request, "All fields are required.")
            return render(request, "FacultySignUp.html")

        # Email format validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Enter a valid email address.")
            return render(request, "FacultySignUp.html")

        # Password confirmation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "FacultySignUp.html")

        # Duplicate check
        if Faculty.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, "FacultySignUp.html")

        # Create account
        Faculty.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password),
            department=department
        )

        messages.success(request, "Account created successfully! You can now sign in.")
        return redirect("faculty_signin")

    return render(request, "FacultySignUp.html")

def faculty_logout(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    request.session.flush()  # Clears all session data
    return redirect("GradeFlow")


def add_comment(request, document_id):
    if request.method == 'POST':
        document = get_object_or_404(ClearanceDocument, id=document_id)
        content = request.POST.get('content', '')
        faculty_id = request.session.get('faculty_id')
        faculty = Faculty.objects.only("id", "first_name", "last_name").get(id=faculty_id)
        student = document.student
    
        

        if content and faculty:
            Comment.objects.create(document=document, faculty=faculty, content=content)
            notify_student(
                student,
                title="New Comment",
                message=f"Faculty added a comment to your submission."
            )
        
        return redirect('homepage')
    
def download_file(request, bucket_name, path):
    """Download a file from Supabase storage."""
    clean_path = path[len(bucket_name) + 1:] if path.startswith(f"{bucket_name}/") else path

    try:
        response = supabase.storage.from_(bucket_name).download(clean_path)
        if not response:
            return HttpResponse("File not found.", status=404)
    except Exception as e:
        return HttpResponse(f"Error downloading file: {e}", status=404)

    filename = os.path.basename(clean_path)
    res = HttpResponse(response, content_type="application/octet-stream")
    res["Content-Disposition"] = f'attachment; filename="{filename}"'
    return res

def preview_file(request, bucket_name, path):
    """
    Return a redirect to a Supabase signed URL (valid short time).
    Only called when faculty clicks 'Preview'.
    """
    if not request.session.get('faculty_id'):
        return redirect('faculty_signin')

    # path: use stored file_path where possible. Here path may be file_path
    try:
        res = supabase.storage.from_(bucket_name).create_signed_url(path, 900)  # 15 minutes
        signed_url = res.get('signedURL') or res.get('signed_url') or res.get('signedUrl')
        if not signed_url:
            return HttpResponse("Could not create signed URL.", status=500)
    except Exception as e:
        return HttpResponse(f"Error creating signed URL: {str(e)}", status=500)

    return redirect(signed_url)


def help_and_support(request):
    faculty = get_logged_in_faculty(request)
    if not faculty:
        return redirect('faculty_signin')
    return render(request, 'HelpAndSupport.html', {'faculty': faculty})
    
