import time
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponse
from django.conf import settings
from student_signup_signin.models import Student
from .models import ClearanceDocument
from supabase import create_client
from Faculty.models import Faculty
from utils.notifications import notify_faculty
from django.contrib.auth.hashers import check_password, make_password


# --- Supabase Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# --- Helper function for summary cards ---
def get_student_summary(student):
    clearances = ClearanceDocument.objects.filter(student=student)
    return {
        'completed_count': clearances.filter(status='Approved').count(),
        'inprogress_count': clearances.filter(status='In Progress').count(),
        'pending_count': clearances.filter(status='Pending').count(),
        'document_count': clearances.count(),
    }

# --- Student Dashboard ---
def student_dashboard(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('signin')

    initials = (student.first_name[0] + student.last_name[0]).upper()
    clearances = ClearanceDocument.objects.filter(student=student)
    summary = get_student_summary(student)

    # Organize clearances in fixed sequence
    clearances_by_dept = get_clearances_by_department(clearances)

    context = {
        'student': student,
        'initials': initials,
        'clearances_by_dept': clearances_by_dept,  # <--- pass this to template
        **summary,
    }
    return render(request, 'studentDashboard.html', context)


# --- Request Clearance ---
def request_clearance(request):
    student_id = request.session.get('student_id')
    
    if not student_id:
        return redirect('signin')

    student = Student.objects.get(id=student_id)
    initials = (student.first_name[0] + student.last_name[0]).upper()
    summary = get_student_summary(student)
    
    staff_list = ['Library', 'Registrar', 'Accounting', 'Academic Adviser']

    if request.method == 'POST':
        document_type = request.POST.get('documentType')
        staff = request.POST.get('staff')
        notes = request.POST.get('notes')
        document_file = request.FILES.get('document')

        file_url = None
        if document_file:
            file_name = f"{student.email_address}/{int(time.time())}_{document_file.name}"
            try:
                supabase.storage.from_(SUPABASE_BUCKET).upload(file_name, document_file.read())
                file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_name}"
            except Exception as e:
                messages.error(request, f"Error uploading file: {e}")
                return redirect('request_clearance')

        # Set initial status: Pending by default
        status = 'Pending'
        # Example: make Registrar submissions show as In Progress immediately
        # if staff == 'Registrar':
        #     status = 'In Progress'

        faculties = Faculty.objects.filter(department=staff)

        for faculty in faculties:
            notify_faculty(
                faculty,
                title="New Clearance Submission",
                message=f"{student.first_name} {student.last_name} submitted a clearance request."
            )

        ClearanceDocument.objects.create(
            student=student,
            document_type=document_type,
            department_name=staff,
            additional_notes=notes,
            file_url=file_url,
            status=status
        )
        messages.success(request, "Document submitted successfully!")
        return redirect('submission_history')

    context = {
        'student': student,
        'initials': initials,
        'staff_list': staff_list,
        **summary,
    }
    return render(request, 'clearanceRequest.html', context)

# --- Submission History ---
def submission_history(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    student = Student.objects.get(id=student_id)
    initials = (student.first_name[0] + student.last_name[0]).upper()
    submissions = ClearanceDocument.objects.filter(student=student).order_by('-time_submitted')
    summary = get_student_summary(student)

    context = {
        'student': student,
        'initials': initials,
        'submissions': submissions,
        'SUPABASE_URL': SUPABASE_URL,
        'SUPABASE_BUCKET': SUPABASE_BUCKET,
        **summary,
    }
    return render(request, 'submissionHistory.html', context)

# --- Logout ---
def student_logout(request):
    request.session.flush()
    logout(request)
    return redirect('signin')

# --- Download file ---
def download_file(request, bucket_name, path):
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

# --- Profile View ---
def profile_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    student = Student.objects.get(id=student_id)
    initials = (student.first_name[0] + student.last_name[0]).upper()

    if request.method == 'POST':
        # Get submitted contact info
        phone_number = request.POST.get('phone_number', '').strip()
        address = request.POST.get('address', '').strip()
        emergency_contact = request.POST.get('emergency_contact', '').strip()

        # Update student record
        student.phone_number = phone_number
        student.address = address
        student.emergency_contact = emergency_contact
        student.save()

        messages.success(request, "Contact information updated successfully!")
        # Refresh student object to show new values
        student.refresh_from_db()

    context = {
        'student': student,
        'initials': initials,
        'completed_count': ClearanceDocument.objects.filter(student=student, status='Approved').count(),
        'inprogress_count': ClearanceDocument.objects.filter(student=student, status='In Progress').count(),
        'pending_count': ClearanceDocument.objects.filter(student=student, status='Pending').count(),
        'document_count': ClearanceDocument.objects.filter(student=student).count(),
    }
    return render(request, 'studentProfile.html', context)


# --- Resubmit Clearance ---
def resubmit_clearance(request, clearance_id):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')
 
    student = Student.objects.get(id=student_id)
    clearance = ClearanceDocument.objects.get(id=clearance_id, student=student)
    staff_list = ['Library', 'Registrar', 'Accounting', 'Academic Adviser']
 
    if request.method == 'POST':
        document_type = request.POST.get('documentType')
        staff = request.POST.get('staff')
        notes = request.POST.get('notes')
        document_file = request.FILES.get('document')
 
        file_url = clearance.file_url
        if document_file:
            file_name = f"{student.email_address}/{int(time.time())}_{document_file.name}"
            try:
                supabase.storage.from_(SUPABASE_BUCKET).upload(file_name, document_file.read())
                file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_name}"
            except Exception as e:
                messages.error(request, f"Error uploading file: {e}")
                return redirect('resubmit_clearance', clearance_id=clearance_id)
            
        faculties = Faculty.objects.filter(department=staff)
        for faculty in faculties:
            notify_faculty(
                faculty,
                title="Resubmitted Clearance Submission",
                message=f"{student.first_name} {student.last_name} with a document type: {document_type}."
            )
 
        # Update existing clearance
        clearance.document_type = document_type
        clearance.department_name = staff
        clearance.additional_notes = notes
        clearance.file_url = file_url
        clearance.status = 'Pending'
        # Example: Registrar submissions go In Progress automatically
        # if staff == 'Registrar':
        #     clearance.status = 'In Progress'
        clearance.save()
 
        messages.success(request, "Document resubmitted successfully!")
        return redirect('student_dashboard')
 
    context = {
        'student': student,
        'initials': (student.first_name[0] + student.last_name[0]).upper(),
        'staff_list': staff_list,
        'clearance': clearance,
        'is_resubmit': True,
    }
    return render(request, 'clearanceRequest.html', context)

# Helper to map clearances by department
def get_clearances_by_department(clearances):
    """
    Returns a dictionary with department names as keys.
    Missing departments will have value None.
    """
    department_sequence = ['Library', 'Registrar', 'Accounting', 'Academic Adviser']
    clearance_dict = {dept: None for dept in department_sequence}
    for c in clearances:
        if c.department_name in clearance_dict:
            clearance_dict[c.department_name] = c
    return clearance_dict

#view profile settings
def settings_profile(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    student = Student.objects.get(id=student_id)
    initials = (student.first_name[0] + student.last_name[0]).upper()
    summary = get_student_summary(student)

    context = {
        'student': student,
        'initials': initials,
        **summary
    }
    return render(request, 'studentProfileSettings.html', context)

#update profile info
def update_profile(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    student = Student.objects.get(id=student_id)

    if request.method == "POST":
        student.phone_number = request.POST.get("phone_number", student.phone_number)
        student.address = request.POST.get("address", student.address)
        student.emergency_contact = request.POST.get("emergency_contact", student.emergency_contact)
        student.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("student_profile_settings")  # or "student_profile"

    # Handle GET requests by redirecting to the profile settings page
    return redirect("student_profile_settings")



#change_password
def change_password(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    student = Student.objects.get(id=student_id)

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Check current password
        if not check_password(current_password, student.password):
            messages.error(request, "Current password is incorrect.")
            return redirect('student_profile_settings')

        # Check matching
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('student_profile_settings')

        # Save new password
        student.password = make_password(new_password)
        student.save()

        messages.success(request, "Password updated successfully!")
        return redirect('student_profile_settings')

    return redirect('student_profile_settings')

# --- HELP & SUPPORT ---
def help_support(request):
    """Render the Help & Support page."""
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    student = Student.objects.get(id=student_id)
    initials = (student.first_name[0] + student.last_name[0]).upper()
    summary = get_student_summary(student)

    context = {
        'student': student,
        'initials': initials,
        **summary,
    }
    return render(request, 'studentHelp&Support.html', context)


def submit_feedback(request):
    """Handle feedback form submission from Help & Support page."""
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    student = Student.objects.get(id=student_id)

    if request.method == "POST":
        feedback_text = request.POST.get("feedback")
        if feedback_text:
            # Example: save to database
            # Feedback.objects.create(student=student, message=feedback_text)
            messages.success(request, "Thank you! Your feedback has been submitted.")
        else:
            messages.error(request, "Please enter feedback before submitting.")
        return redirect('help_support')
    
    return redirect('help_support')


def faq_page(request):
    """Render a separate FAQ page."""
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    student = Student.objects.get(id=student_id)
    initials = (student.first_name[0] + student.last_name[0]).upper()
    summary = get_student_summary(student)

    context = {
        'student': student,
        'initials': initials,
        **summary,
    }
    return render(request, 'faq_page.html', context)

def FAQs_page(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    # Get student
    student = Student.objects.get(id=student_id)

    # Initials for the user circle
    initials = (student.first_name[0] + student.last_name[0]).upper()

    # Dashboard summary (same helper function)
    summary = get_student_summary(student)

    context = {
        'student': student,
        'initials': initials,
        **summary
    }

    return render(request, 'studentFAQs.html', context)