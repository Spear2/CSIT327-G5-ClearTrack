from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from student_signup_signin.models import Student
from .models import ClearanceDocument



def student_dashboard(request):
    student_id = request.session.get('student_id')

    if not student_id:
        return redirect('signin')  # redirect if not logged in

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('signin')

    # ✅ Generate initials (handles empty names safely)
    initials = (
        (student.first_name[0] if student.first_name else '') +
        (student.last_name[0] if student.last_name else '')
    ).upper()

    # ✅ Pass initials and student data to the template
    return render(request, 'studentDashboard.html', {
        'student': student,
        'initials': initials
    })

def student_logout(request):
    logout(request)
    return redirect('signin')  # this should match your login page URL name

sent_requests = []


def request_clearance(request):
    # ✅ Check if student is logged in
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('signin')

    # ✅ Get student object
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('signin')

    # ✅ Prepare initials (for profile circle)
    initials = (student.first_name[0] + student.last_name[0]).upper()

    # Example staff list
    staff_list = ["Registrar", "Guidance Office", "Library", "Accounting Office", "Student Affairs"]

    # ✅ Clear any leftover “Welcome back” messages
    storage = messages.get_messages(request)
    storage.used = True

    # ✅ Handle form submission
    if request.method == "POST":
        document_type = request.POST.get('documentType')
        department_name = request.POST.get('staff')
        notes = request.POST.get('notes')
        file = request.FILES.get('document')  # optional if you handle uploads

        # ✅ Save to your ClearanceDocument table
        clearance = ClearanceDocument.objects.create(
            student=student,
            document_type=document_type,
            department_name=department_name,
            additional_notes=notes,
            file_url=file.name if file else None,
            status='Pending'
        )

        messages.success(request, f"Request successfully sent to {department_name}!")
        return redirect('request_clearance')

    # ✅ Render page (GET request)
    context = {
        'student': student,
        'initials': initials,
        'staff_list': staff_list,
        'completed_count': 0,
        'inprogress_count': 0,
        'pending_count': 0,
        'document_count': ClearanceDocument.objects.filter(student=student).count(),
    }

    return render(request, 'clearanceRequest.html', context)