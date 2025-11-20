from django.shortcuts import render, redirect
from .models import SystemAdmin
from student_signup_signin.models import Student
from Faculty.models import Faculty
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
# Create your views here.

def user_dashboard(request):
    if "admin_email" not in request.session:
        return redirect("admin_login")

    student_count = Student.objects.count()
    faculty_count = Faculty.objects.count()

    return render(request, 'userdashboard.html', {
        "student_count": student_count,
        "faculty_count": faculty_count,
    })

def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Please fill in both email and password.")
            return render(request, "userlogin.html")

        # Find admin by email only
        admin = SystemAdmin.objects.filter(email=email).first()

        if admin:
            # Check password hash
            request.session["admin_email"] = admin.email
            return redirect("admin_dashboard")
            
        else:
            messages.error(request, "Email not found.")

        return render(request, "userlogin.html")
    return render(request, 'userlogin.html')

def user_logout(request):
    request.session.flush()
    return redirect("admin_login")

def manage_students(request):
    if "admin_email" not in request.session:
        return redirect("admin_login")
    
    students = Student.objects.all()
    return render(request, "manage_students.html", {"students": students})

def delete_student(request, id):
    Student.objects.filter(id=id).delete()
    return redirect("manage_students")

def add_student(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email_address = request.POST.get("email_address")
        student_id = request.POST.get("student_id")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("manage_students")

        if Student.objects.filter(email_address=email_address).exists():
            messages.error(request, "Email already exists.")
            return redirect("manage_students")

        Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            email_address=email_address,
            student_id=student_id,
            password=make_password(password)
        )

        messages.success(request, "Student added successfully!")
        return redirect("manage_students")

    return redirect("manage_students")

def manage_faculty(request):
    if "admin_email" not in request.session:
        return redirect("admin_login")
    faculty = Faculty.objects.all()
    return render(request, "manage_faculty.html", {"faculty": faculty})

def delete_faculty(request, id):
    Faculty.objects.filter(id=id).delete()
    return redirect("manage_faculty")


def add_faculty(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        department = request.POST.get("department")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Validate passwords
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            print("Password and Confirm Password does not match!.")
            return redirect("manage_faculty")

        # Optional: Check if email already exists
        if Faculty.objects.filter(email=email).exists():
            messages.error(request, "Email already taken.")
            print("Email already taken")
            return redirect("manage_faculty")

        # Save
        Faculty.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            department=department,
            password=make_password(password)  # in production, hash this!
        )

        messages.success(request, "Faculty added successfully.")
        return redirect("manage_faculty")

    return render(request, "manage_faculty.html")