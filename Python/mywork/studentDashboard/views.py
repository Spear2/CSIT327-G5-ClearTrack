import time
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone

from student_signup_signin.models import Student
from .models import ClearanceDocument

from supabase import create_client


# --- Supabase Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


# ----------------- Helper Summary Counts -----------------
def get_student_summary(student):
    clearances = ClearanceDocument.objects.filter(student=student)

    # Normalize statuses for summary counts
    completed_count = clearances.filter(status__in=['Approved', 'completed']).count()
    inprogress_count = clearances.filter(status='In Progress').count()
    pending_count = clearances.filter(status='Pending').count()

    return {
        'completed_count': completed_count,
        'inprogress_count': inprogress_count,
        'pending_count': pending_count,
        'document_count': clearances.count(),
    }


# ----------------- Student Dashboard -----------------
def student_dashboard(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    student = Student.objects.get(id=student_id)
    initials = (student.first_name[0] + student.last_name[0]).upper()

    department_order = ['Library', 'Registrar', 'Accounting', 'Academic Adviser']

    clearances = ClearanceDocument.objects.filter(student=student)

    # Normalize statuses for template display
    for c in clearances:
        if c.status == "Approved":
            c.status = "completed"

    clearance_dict = {c.department_name: c for c in clearances}

    ordered_clearances = []
    for dept in department_order:
        if dept in clearance_dict:
            ordered_clearances.append(clearance_dict[dept])
        else:
            ordered_clearances.append({
                'department_name': dept,
                'status': 'pending',
                'document_type': 'N/A',
                'additional_notes': 'No submission yet',
                'time_submitted': None,
                'file_url': None
            })

    summary = get_student_summary(student)

    context = {
        'student': student,
        'initials': initials,
        'clearances': ordered_clearances,
        **summary,
    }
    return render(request, 'studentDashboard.html', context)


# ----------------- Submit Clearance Request -----------------
def request_clearance(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    student = Student.objects.get(id=student_id)
    initials = (student.first_name[0] + student.last_name[0]).upper()
    summary = get_student_summary(student)

    staff_list = ['Registrar', 'Library', 'Accounting', 'Academic Adviser']

    if request.method == 'POST':
        document_type = request.POST.get('documentType')
        staff = request.POST.get('staff')
        notes = request.POST.get('notes')
        document_file = request.FILES.get('document')

        file_url = None

        if document_file:
            file_name = f"{student.email_address}/{int(time.time())}_{document_file.name}"

            try:
                supabase.storage.from_(SUPABASE_BUCKET).upload(
                    file_name,
                    document_file.read()
                )
                file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_name}"

            except Exception as e:
                messages.error(request, f"Error uploading file: {e}")
                return redirect('request_clearance')

        ClearanceDocument.objects.create(
            student=student,
            document_type=document_type,
            department_name=staff,
            additional_notes=notes,
            file_url=file_url,
            status='Pending'
        )

        messages.success(request, "Document submitted successfully!")
        return redirect('student_dashboard')

    context = {
        'student': student,
        'initials': initials,
        'staff_list': staff_list,
        **summary,
    }
    return render(request, 'clearanceRequest.html', context)


# ----------------- Submission History -----------------
def submission_history(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    student = Student.objects.get(id=student_id)
    initials = (student.first_name[0] + student.last_name[0]).upper()
    submissions = ClearanceDocument.objects.filter(student=student).order_by('-time_submitted')

    # Normalize statuses for template display
    for s in submissions:
        if s.status == "Approved":
            s.status = "completed"

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


# ----------------- Logout -----------------
def student_logout(request):
    logout(request)
    return redirect('signin')


# ----------------- Download File -----------------
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


# ----------------- Student Profile -----------------
def profile_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    student = Student.objects.get(id=student_id)
    initials = (student.first_name[0] + student.last_name[0]).upper()

    context = {
        'student': student,
        'initials': initials,
        **get_student_summary(student)
    }
    return render(request, 'studentProfile.html', context)


# ----------------- Resubmit Clearance (if rejected) -----------------
def resubmit_clearance(request, clearance_id):
    clearance = get_object_or_404(ClearanceDocument, id=clearance_id)

    if request.method == 'POST':
        new_file = request.FILES.get('new_document')

        if new_file:
            file_name = f"{clearance.student.email_address}/{int(time.time())}_{new_file.name}"

            supabase.storage.from_(SUPABASE_BUCKET).upload(
                file_name,
                new_file.read(),
                file_options={"upsert": True}
            )

            new_file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_name}"
            clearance.file_url = new_file_url

        clearance.status = "In Progress"
        clearance.time_submitted = timezone.now()
        clearance.additional_notes = "Resubmitted by student."

        clearance.save()

        messages.success(request, "File resubmitted successfully!")
        return redirect('student_dashboard')

    return redirect('student_dashboard')
