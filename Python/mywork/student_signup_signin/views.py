from django.shortcuts import render, redirect
from .models import Student
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

def signup(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email_address = request.POST['email_address']
        student_id = request.POST['student_id']
        password = request.POST['password'] 
        confirm_password = request.POST['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        # Hash the password
        hashed_password = make_password(password)

        # Create the student
        Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            email_address=email_address,
            student_id=student_id,
            password=hashed_password
        )

        messages.success(request, "Signup successful! You can now sign in.")
        return redirect('signin')

    return render(request,'signup.html')


def signin(request):
    if request.method == "POST":
        email_address = request.POST['email_address']
        password = request.POST['password']

        # Check if student exists
        try:
            student = Student.objects.get(email_address=email_address)
        except Student.DoesNotExist:
            messages.error(request, "Email not found. Please sign up first.")
            return redirect('signin')

        # Check password
        if check_password(password, student.password):
            # Password is correct
            messages.success(request, f"Welcome back, {student.first_name}!")
            # You can set a session here if needed
            request.session['student_id'] = student.id
            request.session["student_email"] = student.email_address
            request.session.set_expiry(0)  # session ends on browser close
            return redirect('student_dashboard')  # replace with your dashboard/home page
        else:
            messages.error(request, "Incorrect password. Please try again.")
            return redirect('signin')

    return render(request, 'signin.html')

def student_dashboard(request):
    return render(request, 'dashboard.html')
