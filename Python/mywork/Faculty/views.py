from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from .models import Faculty, Comment
from django.contrib.auth import authenticate, login
from studentDashboard.models import ClearanceDocument
from django.db.models import Q, Case, When, Value, IntegerField
from django.utils import timezone
from datetime import timedelta

DEPARTMENT_MAP = {
    "library": "Library",
    "accounting": "Accounting",
    "acadaffairs": "Academic Affairs",
    "studaffairs": "Student Affairs",
    "itDepartment": "IT Department",
    "plant": "Physical Plant",
}

# Create your views here.
def home(request):
    return render(request, 'LandingPage.html')

def update_status(request, document_id):
    
    if request.method == 'POST':
       
        document = get_object_or_404(ClearanceDocument, id=document_id)
        new_status = request.POST.get('status')

        faculty_id = request.session.get('faculty_id')
        faculty = Faculty.objects.get(id=faculty_id)
        faculty_department = DEPARTMENT_MAP.get(faculty.department,"").lower()

        if faculty_department == document.department_name.lower():
            print("status is updated")
            document.status = new_status
            document.save()
            
        else:
            print("Status won't changed")

    return redirect('homepage')

def homepage(request):
    faculty = None
    initials = ""
    requests = []
    faculty_department = ""
    selected_status = request.GET.get('status','All')
    selected_department = request.GET.get('department', 'All_Department')
    search_query = request.GET.get('search', '')
    selected_date = request.GET.get('date_filter', 'All_Time')
    count_Pending = 0
    count_Approved = 0
    count_Reject = 0

    count_Pending += ClearanceDocument.objects.filter(status='Pending').count()
    count_Approved += ClearanceDocument.objects.filter(status='Approved').count()
    count_Reject += ClearanceDocument.objects.filter(status='Rejected').count()

    
    requests = ClearanceDocument.objects.select_related('student')

    if selected_status != 'All':
        requests = requests.filter(status=selected_status)
    
    if selected_department != 'All_Department':
        requests = requests.filter(department_name=selected_department)

    if search_query:
        requests = requests.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__student_id__icontains=search_query)
        )
    

    requests = requests.annotate(
        status_priority=Case(
            When(status='Pending', then=Value(0)),
            When(status='Approved', then=Value(1)),
            When(status='Rejected', then=Value(2)),
            default=Value(3),
            output_field=IntegerField()
        )
    ).order_by('status_priority', '-time_submitted')

    
    now = timezone.now()
    if selected_date == 'Last_7_Days':
        requests = requests.filter(time_submitted__gte=now-timedelta(days=7))
    elif selected_date == 'Last_30_Days':
        requests = requests.filter(time_submitted__gte=now-timedelta(days=30))
    elif selected_date == 'This_Semester':
        month = now.month
        if month >= 6:
            semester_start = timezone.datetime(now.year, 6, 1, tzinfo=timezone.get_current_timezone())
        else:
            semester_start = timezone.datetime(now.year, 11, 1, tzinfo=timezone.get_current_timezone())
        requests = requests.filter(time_submitted__gte=semester_start)
    faculty_id = request.session.get("faculty_id")
    if faculty_id:
        try:
            faculty = Faculty.objects.get(id=faculty_id)
            initials = f"{faculty.first_name[0]}{faculty.last_name[0]}".upper()
            faculty_department = DEPARTMENT_MAP.get(faculty.department,"").lower()
        except Faculty.DoesNotExist:
            pass

    context = {
        "faculty": faculty,
        "initials": initials,
        "requests": requests,
        "faculty_department": faculty_department,
        "selected_status": selected_status,
        "selected_department": selected_department,
        "selected_date": selected_date,
        "count_Approved": count_Approved,
        "count_Reject": count_Reject,
        "count_Pending": count_Pending,
    }

    return render(request, "Hompage.html", context)

def faculty_signin(request):
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
    request.session.flush()  # Clears all session data
    return redirect("GradeFlow")

def faculty_settings(request):
    return render(request, "Faculty_Profile.html")

def add_comment(request, document_id):
    if request.method == 'POST':
        document = get_object_or_404(ClearanceDocument, id=document_id)
        content = request.POST.get('content', '')
        faculty_id = request.session.get('faculty_id')
        faculty = Faculty.objects.get(id=faculty_id) if faculty_id else None
    
        

        if content and faculty:
            Comment.objects.create(document=document, faculty=faculty, content=content)
        
        return redirect('homepage')
    
