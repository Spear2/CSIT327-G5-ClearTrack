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
        if staff == 'Registrar':
            status = 'In Progress'

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

        # Update existing clearance
        clearance.document_type = document_type
        clearance.department_name = staff
        clearance.additional_notes = notes
        clearance.file_url = file_url
        clearance.status = 'Pending'
        # Example: Registrar submissions go In Progress automatically
        if staff == 'Registrar':
            clearance.status = 'In Progress'
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

