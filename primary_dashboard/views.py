# EVENTS FEATURE
from django.contrib.auth.decorators import login_required

# EVENTS FEATURE
@login_required
def events_list(request):
    from .models import Event
    events = Event.objects.all().order_by('-date')
    return render(request, 'primary_dashboard/events.html', {'events': events})

@login_required
def create_event(request):
    from .forms import EventForm
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('primary_dashboard:events_list')
    else:
        form = EventForm()
    return render(request, 'primary_dashboard/create_event.html', {'form': form})

@login_required
def edit_event(request, event_id):
    from .models import Event
    from .forms import EventForm
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('primary_dashboard:events_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'primary_dashboard/edit_event.html', {'form': form, 'event': event})

@login_required
def delete_event(request, event_id):
    from .models import Event
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('primary_dashboard:events_list')
    return render(request, 'primary_dashboard/delete_event.html', {'event': event})
from django.http import FileResponse, HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.template.loader import render_to_string
import tempfile
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Class, Subject, Student, Grade, Mark, Report, Message, Parent, SchoolSettings
from .forms import (
    ClassForm, SubjectForm, StudentForm, GradeForm, MarkForm, 
    ReportForm, MessageForm, MarksSelectForm, ReportSelectForm, SchoolSettingsForm
)
from .forms import StudentModalForm
from .forms import NotificationForm
from .models import Notification
from django.db.models import Q
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.db.models import Avg, Sum
from accounts.models import Teacher
from django import forms
from datetime import datetime


# PDF generation for student report using HTML template (like secondary_dashboard)
@login_required
def student_report_pdf(request, student_id, class_id, term, year):
    student = get_object_or_404(Student, id=student_id)
    class_obj = get_object_or_404(Class, id=class_id)
    report = Report.objects.filter(student=student, term=term, year=year).first()
    marks = Mark.objects.filter(student=student, term=term, year=year)
    total_score = sum(mark.score for mark in marks)
    num_subjects = marks.count()
    average_score = total_score / num_subjects if num_subjects > 0 else 0
    # Calculate position
    all_students = Student.objects.filter(current_class=class_obj)
    student_totals = []
    for s in all_students:
        s_marks = Mark.objects.filter(student=s, term=term, year=year)
        s_total = sum(m.score for m in s_marks)
        student_totals.append((s.id, s_total))
    student_totals.sort(key=lambda x: x[1], reverse=True)
    position = next((i+1 for i, (sid, _) in enumerate(student_totals) if sid == student.id), None)
    total_students = all_students.count()
    # School settings
    settings = SchoolSettings.objects.first()
    # Get all grades for the grading system table
    grades = Grade.objects.all().order_by('-min_score')
    # Render HTML
    html_string = render_to_string('primary_dashboard/report_pdf.html', {
        'student': student,
        'marks': marks,
        'term': term,
        'year': year,
        'total_score': total_score,
        'average_score': average_score,
        'position': position,
        'total_students': total_students,
        'report': report,
        'settings': settings,
        'grades': grades,
    })
    # Generate PDF from HTML
    try:
        import weasyprint
    except ImportError:
        return HttpResponse("WeasyPrint is required to generate PDF. Please install it.")
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as output:
        weasyprint.HTML(string=html_string).write_pdf(output.name)
        output.seek(0)
        pdf = output.read()
    os.unlink(output.name)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=student_report_{student.id}_{term}_{year}.pdf'
    return response
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Class, Subject, Student, Grade, Mark, Report, Message, Parent, SchoolSettings
from .forms import (
    ClassForm, SubjectForm, StudentForm, GradeForm, MarkForm, 
    ReportForm, MessageForm, MarksSelectForm, ReportSelectForm, SchoolSettingsForm
)
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.http import HttpResponse,JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.db.models import Avg, Sum
from accounts.models import Teacher
from django import forms
from datetime import datetime

@login_required
def student_report_view(request, student_id, class_id, term, year):
    student = get_object_or_404(Student, id=student_id)
    class_obj = get_object_or_404(Class, id=class_id)

    # Check if user is parent and student is their child
    if hasattr(request.user, 'parent') and request.user.parent:
        if student.parent != request.user.parent:
            from django.http import Http404
            raise Http404("You are not authorized to view this report.")
    # Get or create the report for this student, term, and year
    report, _ = Report.objects.get_or_create(student=student, term=term, year=year)
    # Get marks for this student, term, and year
    marks = Mark.objects.filter(student=student, term=term, year=year)
    total_marks = sum(mark.score for mark in marks)
    num_subjects = marks.count()
    average = total_marks / num_subjects if num_subjects > 0 else 0
    # Get overall grade based on average
    overall_grade = Grade.objects.filter(min_score__lte=average, max_score__gte=average).first()

    # Calculate position in class
    all_students = Student.objects.filter(current_class=class_obj)
    student_totals = []
    for s in all_students:
        s_marks = Mark.objects.filter(student=s, term=term, year=year)
        s_total = sum(m.score for m in s_marks)
        student_totals.append((s.id, s_total))
    # Sort by total descending, assign position
    student_totals.sort(key=lambda x: x[1], reverse=True)
    position = next((i+1 for i, (sid, _) in enumerate(student_totals) if sid == student.id), None)

    settings = SchoolSettings.objects.first()
    total_students = all_students.count()
    context = {
        'student': student,
        'class_obj': class_obj,
        'term': term,
        'year': year,
        'report': report,
        'marks': marks,
        'total_marks': total_marks,
        'average': average,
        'overall_grade': overall_grade,
        'position': position,
        'total_students': total_students,
        'settings': settings,
    }

    if hasattr(request.user, 'parent') and request.user.parent:
        return render(request, 'primary_dashboard/parent_student_report.html', context)

    # Handle comment saving for non-parents
    if request.method == 'POST':
        class_teacher_comment = request.POST.get('class_teacher_comment', '')
        headteacher_comment = request.POST.get('headteacher_comment', '')
        report.class_teacher_comment = class_teacher_comment
        report.headteacher_comment = headteacher_comment
        report.save()
        messages.success(request, 'Comments saved successfully!')
        # Redirect to avoid resubmission
        return redirect('primary_dashboard:student_report', student_id=student.id, class_id=class_obj.id, term=term, year=year)

    return render(request, 'primary_dashboard/student_report.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Class, Subject, Student, Grade, Mark, Report, Message, Parent, SchoolSettings
from .forms import (
    ClassForm, SubjectForm, StudentForm, GradeForm, MarkForm, 
    ReportForm, MessageForm, MarksSelectForm, ReportSelectForm, SchoolSettingsForm
)
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.http import HttpResponse,JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.db.models import Avg, Sum
from accounts.models import Teacher
from django import forms
from datetime import datetime

def get_subjects(request):
    subjects = Subject.objects.all()
    subjects_data = [{'id': subject.id, 'name': subject.name} for subject in subjects]
    return JsonResponse(subjects_data, safe=False)

@login_required
def classes_view(request):
    # Provide a class-management UI similar to secondary_dashboard.class_management
    # Show a left list of classes and a right panel listing students in the selected class.
    teacher = request.user

    # Handle class creation (existing behavior)
    if request.method == 'POST' and request.POST.get('action') == 'create_class':
        form = ClassForm(request.POST, teacher=teacher)
        if form.is_valid():
            class_instance = form.save(commit=False)
            class_instance.class_teacher = teacher
            class_instance.save()
            form.save_m2m()  # Needed for ManyToMany fields
            messages.success(request, 'Class added successfully!')
            return redirect('primary_dashboard:classes')
    else:
        form = ClassForm(teacher=teacher)

    # Build forms (classes) list and determine selected form
    forms_qs = Class.objects.all().order_by('name')
    selected_id = request.GET.get('class_id')
    selected_form = None
    if selected_id:
        try:
            selected_form = Class.objects.get(id=selected_id)
        except Class.DoesNotExist:
            selected_form = None

    if not selected_form:
        selected_form = forms_qs.first()

    students = Student.objects.filter(current_class=selected_form) if selected_form else Student.objects.none()

    # Use StudentModalForm for the Add Student modal (collects plain parent name fields)
    student_form = StudentModalForm()

    context = {
        'forms': forms_qs,
        'selected_form': selected_form,
        'students': students,
        'form': student_form,
    }
    return render(request, 'primary_dashboard/class_management.html', context)

@login_required
def dashboard(request):
    teacher_count = Teacher.objects.count()
    student_count = Student.objects.count()
    parent_count = Parent.objects.count()
    
    context = {
        'teacher_count': teacher_count,
        'student_count': student_count,
        'parent_count': parent_count,
    }
    return render(request, 'primary_dashboard/dashboard.html', context)


@login_required
def home(request):
    """Primary dashboard home page (summary)."""
    # Counts
    teacher_count = Teacher.objects.count()
    student_count = Student.objects.count()
    class_count = Class.objects.count()

    # Recent activities: use Event model if available
    try:
        from .models import Event
        recent_activities = Event.objects.all().order_by('-date')[:6]
    except Exception:
        recent_activities = []

    # Performance summary: average marks per class
    class_performance = []
    classes = Class.objects.all()
    for c in classes:
        avg = Mark.objects.filter(student__current_class=c).aggregate(avg=Avg('score'))['avg']
        class_performance.append({
            'class_name': getattr(c, 'name', str(c)),
            'average_marks': avg or 0
        })

    # Upcoming events
    from datetime import date
    try:
        upcoming_events = Event.objects.filter(date__gte=date.today()).order_by('date')[:5]
    except Exception:
        upcoming_events = []

    context = {
        'teacher_count': teacher_count,
        'student_count': student_count,
        'class_count': class_count,
        'recent_activities': recent_activities,
        'class_performance': class_performance,
        'upcoming_events': upcoming_events,
    }
    return render(request, 'primary_dashboard/home.html', context)


@login_required
def settings_view(request):
    school_settings, created = SchoolSettings.objects.get_or_create(id=1)
    # Subject form
    if request.method == 'POST' and 'subject_submit' in request.POST:
        subject_form = SubjectForm(request.POST)
        if subject_form.is_valid():
            subject = subject_form.save()
            # Add the new subject to all classes
            for class_obj in Class.objects.all():
                class_obj.subjects.add(subject)
            messages.success(request, 'Subject added successfully!')
            return redirect('primary_dashboard:settings')
    else:
        subject_form = SubjectForm()

    # Grade form
    if request.method == 'POST' and 'grade_submit' in request.POST:
        grade_form = GradeForm(request.POST)
        if grade_form.is_valid():
            grade_form.save()
            messages.success(request, 'Grade added successfully!')
            return redirect('primary_dashboard:settings')
    else:
        grade_form = GradeForm()

    # Settings form
    if request.method == 'POST' and 'settings_submit' in request.POST:
        # If no new logo uploaded, keep the old one
        post = request.POST.copy()
        files = request.FILES.copy()
        if not files.get('logo') and school_settings.logo:
            # Remove logo from cleaned_data so it doesn't get cleared
            files['logo'] = school_settings.logo
        settings_form = SchoolSettingsForm(post, files, instance=school_settings)
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, 'School settings updated successfully.')
            return redirect('primary_dashboard:settings')
    else:
        settings_form = SchoolSettingsForm(instance=school_settings)

    subjects = Subject.objects.all()
    grades = Grade.objects.all()
    return render(request, 'primary_dashboard/settings.html', {
        'settings_form': settings_form,
        'subject_form': subject_form,
        'subjects': subjects,
        'grade_form': grade_form,
        'grades': grades,
    })

from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model

def parent_login(request):
    # This view is now deprecated, parent login is handled in accounts app
    return redirect('accounts:parent_login')

def parent_dashboard(request):
    # Render the primary parent dashboard template
    from accounts.context_processors import parent_dashboard_context
    context = parent_dashboard_context(request)
    return render(request, 'primary_dashboard/parent_dashboard.html', context)

@login_required
def save_marks(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        student_id = request.POST.get('student_id')
        subject_id = request.POST.get('subject_id')
        score = request.POST.get('score')
        term = request.POST.get('term')
        year = request.POST.get('year')

        try:
            student = Student.objects.get(id=student_id)
            subject = Subject.objects.get(id=subject_id)

            # Calculate grade based on score
            grade = None
            if score:
                try:
                    score_int = int(score)
                    grade = Grade.objects.filter(min_score__lte=score_int, max_score__gte=score_int).first()
                except ValueError:
                    pass  # Keep grade as None if score is not a valid integer

            # Use update_or_create to either update an existing mark or create a new one
            mark, created = Mark.objects.update_or_create(
                student=student,
                subject=subject,
                term=term,
                year=year,
                defaults={'score': score, 'grade': grade}
            )
            return JsonResponse({'status': 'success', 'message': 'Mark and grade saved successfully.'})
        except (Student.DoesNotExist, Subject.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Student or Subject not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)
@login_required
def class_detail_view(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)

    # For GET requests, show the shared classes management page instead of a standalone detail page.
    # This makes /primary_dashboard/class/1/ behave the same as /primary_dashboard/classes/?class_id=1
    if request.method == 'GET':
        return redirect(reverse('primary_dashboard:classes') + f'?class_id={class_id}')

    if request.method == 'POST':
        # Support two submission patterns:
        # - Standard StudentForm (select existing parent/current_class)
        # - Modal quick form which posts parent_first_name/... fields (StudentModalForm)
        if 'parent_first_name' in request.POST or 'parent_last_name' in request.POST:
            modal_form = StudentModalForm(request.POST)
            if modal_form.is_valid():
                # Create or provision a User account for the parent because Parent.user is required.
                from django.contrib.auth import get_user_model
                User = get_user_model()
                parent_email = modal_form.cleaned_data.get('parent_email') or ''
                parent_phone = modal_form.cleaned_data.get('parent_phone') or ''

                # Build a unique username from the parent's full name
                first_name = modal_form.cleaned_data.get('parent_first_name', '')
                middle_name = modal_form.cleaned_data.get('parent_middle_name', '')
                last_name = modal_form.cleaned_data.get('parent_last_name', '')

                # Concatenate names, filtering out empty parts
                name_parts = [name for name in [first_name, middle_name, last_name] if name]
                base_username = '.'.join(name_parts).lower() or 'parent'
                
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}.{counter}"
                    counter += 1

                user = User.objects.create(username=username, email=parent_email)
                # Don't set a usable password for this auto-created account.
                try:
                    user.set_unusable_password()
                except Exception:
                    pass
                user.save()

                # create parent record linked to the created user
                parent = Parent.objects.create(
                    user=user,
                    first_name=modal_form.cleaned_data.get('parent_first_name'),
                    middle_name=modal_form.cleaned_data.get('parent_middle_name') or '',
                    last_name=modal_form.cleaned_data.get('parent_last_name'),
                    phone=parent_phone,
                    email=parent_email
                )
                # create student and assign class and parent
                student = Student.objects.create(
                    first_name=modal_form.cleaned_data.get('first_name'),
                    middle_name=modal_form.cleaned_data.get('middle_name') or '',
                    last_name=modal_form.cleaned_data.get('last_name'),
                    gender=modal_form.cleaned_data.get('gender'),
                    date_of_birth=modal_form.cleaned_data.get('date_of_birth'),
                    current_class=class_obj,
                    parent=parent
                )
                messages.success(request, f'Student added to {class_obj.name} successfully!')
                return redirect('primary_dashboard:class_detail', class_id=class_id)
            else:
                # Show modal form errors
                error_list = []
                for field, errors in modal_form.errors.items():
                    for error in errors:
                        error_list.append(f"{field}: {error}")
                if error_list:
                    messages.error(request, "Form submission failed:<br>" + "<br>".join(error_list))
        else:
            form = StudentForm(request.POST, teacher=request.user)
            if form.is_valid():
                student = form.save(commit=False)  # Use commit=False to set current_class before saving
                student.current_class = class_obj
                student.save()
                messages.success(request, f'Student added to {class_obj.name} successfully!')
                return redirect('primary_dashboard:class_detail', class_id=class_id)
            else:
                # Show form errors to the user
                error_list = []
                for field, errors in form.errors.items():
                    for error in errors:
                        error_list.append(f"{form.fields[field].label if field in form.fields else field}: {error}")
                if error_list:
                    messages.error(request, "Form submission failed:<br>" + "<br>".join(error_list))
    else:
        form = StudentForm(teacher=request.user)

    students = Student.objects.filter(current_class=class_obj)
    parents = Parent.objects.all()
    context = {
        'class_obj': class_obj,
        'students': students,
        'form': form,
        'parents': parents,
    }
    return render(request, 'primary_dashboard/classes.html', context)

@login_required
def delete_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id, class_teacher=request.user)
    # Handle students by setting current_class to None
    Student.objects.filter(current_class=class_obj).update(current_class=None)
    class_obj.delete()
    messages.success(request, 'Class deleted successfully!')
    return redirect('primary_dashboard:classes')

@login_required
def edit_class(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id, class_teacher=request.user)
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_obj, teacher=request.user)
        if form.is_valid():
            form.save()
            form.save_m2m()
            messages.success(request, 'Class updated successfully!')
            return redirect('primary_dashboard:classes')
    else:
        form = ClassForm(instance=class_obj, teacher=request.user)
    return render(request, 'primary_dashboard/edit_class.html', {'form': form})

@login_required
def subjects_view(request):
    teacher = request.user
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully!')
            return redirect('primary_dashboard:subjects')
    else:
        form = SubjectForm()
    
    subjects = Subject.objects.all()
    return render(request, 'primary_dashboard/subjects.html', {'form': form, 'subjects': subjects})

@login_required
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, 'Subject deleted successfully!')
    return redirect('primary_dashboard:subjects')

@login_required
def edit_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully!')
            return redirect('primary_dashboard:subjects')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'primary_dashboard/edit_subject.html', {'form': form})

@login_required
def students_view(request):
    teacher = request.user
    classes = Class.objects.filter(class_teacher=teacher)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, teacher=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully!')
            return redirect('primary_dashboard:students')
    else:
        form = StudentForm(teacher=teacher)
        
    students = Student.objects.filter(current_class__in=classes)
    return render(request, 'primary_dashboard/students.html', {'form': form, 'students': students})


@login_required
def timetable_view(request):
    """Show timetables by form. Admins can upload; teachers see timetables for their classes."""
    # Use primary app Timetable model so primary uploads go into primary_dashboard_timetable table
    from .models import Timetable
    # Handle upload (admin/staff only)
    if request.method == 'POST':
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'You do not have permission to upload timetables.')
            return redirect('primary_dashboard:timetable')

        form_choice = request.POST.get('form')
        uploaded_file = request.FILES.get('file')
        if form_choice and uploaded_file:
            tt = Timetable(form=form_choice, file=uploaded_file, uploaded_by=request.user)
            tt.save()
            messages.success(request, 'Timetable uploaded successfully.')
            return redirect('primary_dashboard:timetable')
        else:
            messages.error(request, 'Please select a class/form and a file to upload.')
            return redirect('primary_dashboard:timetable')

    # GET: gather timetables per form
    forms_data = []
    for i in range(1, 8):
        form_num = str(i)
        q = Timetable.objects.filter(form=form_num).order_by('-uploaded_at')
        forms_data.append({'num': form_num, 'timetables': q})

    # If user is a class teacher, determine which class names they teach
    teacher_forms = set()
    try:
        teacher_classes = Class.objects.filter(class_teacher=request.user).values_list('name', flat=True)
        teacher_forms = set(teacher_classes)
    except Exception:
        teacher_forms = set()

    return render(request, 'primary_dashboard/timetable.html', {
        'forms_data': forms_data,
        'teacher_forms': teacher_forms,
    })


@login_required
def teachers_view(request):
    """Render a list of teachers for the primary dashboard."""
    try:
        teachers = Teacher.objects.all()
    except Exception:
        teachers = []

    return render(request, 'primary_dashboard/teachers.html', {'teachers': teachers})

@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if student.current_class:
        class_id = student.current_class.id
        if student.current_class.class_teacher == request.user:
            student.delete()
            messages.success(request, 'Student deleted successfully!')
            return redirect('primary_dashboard:class_detail', class_id=class_id)
        else:
            messages.error(request, 'You are not authorized to delete this student.')
            return redirect('primary_dashboard:class_detail', class_id=class_id)
    else:
        messages.error(request, 'Student has no assigned class.')
        return redirect('primary_dashboard:students')

@login_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    class_id = student.current_class.id
    if student.current_class.class_teacher != request.user:
        messages.error(request, 'You are not authorized to edit this student.')
        return redirect('primary_dashboard:class_detail', class_id=class_id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student, teacher=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('primary_dashboard:class_detail', class_id=class_id)
    else:
        form = StudentForm(instance=student, teacher=request.user)
    return render(request, 'primary_dashboard/edit_student.html', {'form': form})

@login_required
def grades_view(request):
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade added successfully!')
            return redirect('primary_dashboard:grades')
    else:
        form = GradeForm()
    
    grades = Grade.objects.all()
    return render(request, 'primary_dashboard/grades.html', {'form': form, 'grades': grades})

@login_required
def delete_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    grade.delete()
    messages.success(request, 'Grade deleted successfully!')
    return redirect('primary_dashboard:grades')

@login_required
def edit_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade updated successfully!')
            return redirect('primary_dashboard:grades')
    else:
        form = GradeForm(instance=grade)
    return render(request, 'primary_dashboard/edit_grade.html', {'form': form})

@login_required
def marks_select_view(request):
    # Ensure the logged-in user is a teacher
    if not isinstance(request.user, Teacher):
        messages.error(request, "You are not authorized to view this page.")
        return redirect('accounts:teacher_login')

    if request.method == 'POST':
        form = MarksSelectForm(request.POST)
        # Populate subject queryset for validation with all subjects
        form.fields['subject'].queryset = Subject.objects.all()

        if form.is_valid():
            class_name = form.cleaned_data['class_name']
            subject = form.cleaned_data['subject']
            term = form.cleaned_data['term']
            year = form.cleaned_data['year']
            return redirect('primary_dashboard:marks_entry', class_id=class_name.id, subject_id=subject.id, term=term, year=year)
    else:
        form = MarksSelectForm()
        
    return render(request, 'primary_dashboard/marks_select.html', {'form': form})

@login_required
def get_grade_for_score(request):
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        score = request.GET.get('score')
        if score:
            try:
                score = int(score)
                grade = Grade.objects.filter(min_score__lte=score, max_score__gte=score).first()
                if grade:
                    return JsonResponse({
                        'grade_name': grade.name,
                        'grade_range': f'{grade.min_score}-{grade.max_score}'
                    })
                else:
                    return JsonResponse({'grade_name': '-', 'grade_range': ''})
            except ValueError:
                return JsonResponse({'grade_name': '-', 'grade_range': ''})
        return JsonResponse({'grade_name': '-', 'grade_range': ''})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def marks_entry_view(request, class_id, subject_id, term, year):
    class_obj = get_object_or_404(Class, id=class_id)
    subject_obj = get_object_or_404(Subject, id=subject_id)
    students = Student.objects.filter(current_class=class_obj)
    
    from .models import Grade
    grades_exist = Grade.objects.exists()
    if request.method == 'POST':
        forms = [MarkForm(request.POST, prefix=str(student.id)) for student in students]
        grades_for_students = []
        if all(form.is_valid() for form in forms):
            from .models import Grade
            for form in forms:
                mark = form.save(commit=False)
                student_id = form.prefix
                student = Student.objects.get(id=student_id)
                mark.student = student
                mark.subject = subject_obj
                mark.term = term
                mark.year = year
                # Automatically assign grade based on score
                score = form.cleaned_data.get('score')
                grade = Grade.objects.filter(min_score__lte=score, max_score__gte=score).first()
                mark.grade = grade
                mark.save()
                grades_for_students.append(grade)
            return redirect('primary_dashboard:marks_select')
        else:
            # If not valid, try to show grades for entered scores
            from .models import Grade
            for form in forms:
                score = form.data.get(f'{form.prefix}-score')
                try:
                    score = int(score)
                except (TypeError, ValueError):
                    score = None
                grade = None
                if score is not None:
                    grade = Grade.objects.filter(min_score__lte=score, max_score__gte=score).first()
                grades_for_students.append(grade)
    else:
        forms = []
        grades_for_students = []
        from .models import Mark
        for student in students:
            try:
                mark = Mark.objects.get(student=student, subject=subject_obj, term=term, year=year)
                forms.append(MarkForm(instance=mark, prefix=str(student.id)))
                grades_for_students.append(mark.grade)
            except Mark.DoesNotExist:
                forms.append(MarkForm(initial={'student': student, 'subject': subject_obj, 'term': term, 'year': year}, prefix=str(student.id)))
                grades_for_students.append(None)

    context = {
        'forms': zip(students, forms, grades_for_students),
        'class_obj': class_obj,
        'subject_obj': subject_obj,
        'term': term,
        'year': year,
        'grades_exist': grades_exist,
    }
    return render(request, 'primary_dashboard/marks_entry_form.html', context)

@login_required
def report_select(request):
    if request.method == 'POST':
        class_id = request.POST.get('class')
        term = request.POST.get('term')
        year = request.POST.get('year')

        if not all([class_id, term, year]):
            messages.error(request, "Please select class, term, and year.")
            return redirect('primary_dashboard:report_select')

        return redirect('primary_dashboard:view_class_report', class_id=class_id, term=term, year=year)

    classes = Class.objects.all()
    current_year = datetime.now().year
    YEAR_CHOICES = [(year, year) for year in range(current_year - 1, current_year + 5)]
    
    context = {
        'classes': classes,
        'terms': ['Term 1', 'Term 2', 'Term 3'],
        'years': [year for year, _ in YEAR_CHOICES]
    }
    return render(request, 'primary_dashboard/report_select.html', context)


@login_required
def report_view(request, class_id, term, year):
    class_obj = get_object_or_404(Class, id=class_id)
    students = Student.objects.filter(current_class=class_obj)
    settings = SchoolSettings.objects.first()
    context = {
        'class_obj': class_obj,
        'students': students,
        'term': term,
        'year': year,
        'class_id': class_id,
        'settings': settings,
    }
    return render(request, 'primary_dashboard/report.html', context)

@login_required
def print_all_reports(request, class_id, term, year):
    # This view is intended to generate a PDF for all reports.
    # The logic for PDF generation will be implemented here.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reports_{class_id}_{term}_{year}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    p.drawString(100, 750, f"Reports for Class ID: {class_id}, Term: {term}, Year: {year}")
    p.showPage()
    p.save()
    return response

@login_required
def message_view(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            message_text = form.cleaned_data['message']
            
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                subject=subject,
                message=message_text,
                is_delivered=True
            )
            messages.success(request, 'Message sent successfully!')
            return redirect('primary_dashboard:messages')
    else:
        form = MessageForm()

    sent_messages = Message.objects.filter(sender=request.user).order_by('-timestamp')

    return render(request, 'primary_dashboard/message.html', {'form': form, 'sent_messages': sent_messages})

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.sender == request.user or message.recipient == request.user:
        message.delete()
        messages.success(request, 'Message deleted successfully!')
    else:
        messages.error(request, 'You are not authorized to delete this message.')
    return redirect('primary_dashboard:messages')


@login_required
def notifications_view(request):
    """Notifications page: admin can post notifications (to all teachers or a class).
    Teachers see relevant notifications.
    """
    user = request.user

    # Handle new notification (admin/staff only)
    if request.method == 'POST':
        if not (user.is_staff or user.is_superuser):
            messages.error(request, 'You do not have permission to send notifications.')
            return redirect('primary_dashboard:notifications')

        form = NotificationForm(request.POST)
        if form.is_valid():
            notif = form.save(commit=False)
            notif.created_by = user
            notif.save()
            messages.success(request, 'Notification sent successfully.')
            return redirect('primary_dashboard:notifications')
    else:
        form = NotificationForm()

    # Determine notifications visible to this user
    if user.is_staff or user.is_superuser:
        notifications = Notification.objects.filter(is_active=True).order_by('-created_at')
    else:
        # Teachers: show notifications targeted to all or to classes they teach
        teacher_classes = Class.objects.filter(class_teacher=user).values_list('id', flat=True)
        notifications = Notification.objects.filter(
            is_active=True
        ).filter(
            Q(target_type='all_teachers') | Q(target_class__id__in=teacher_classes)
        ).order_by('-created_at')

    # Mark displayed notifications as read for this user (so badges update)
    try:
        unread_qs = notifications.exclude(read_by=user)
        for n in unread_qs:
            n.read_by.add(user)
    except Exception:
        pass

    return render(request, 'primary_dashboard/notifications.html', {
        'notifications': notifications,
        'form': form,
    })


@login_required
def marks_view(request):
    if request.method == 'POST':
        class_id = request.POST.get('class')
        subject_id = request.POST.get('subject')
        term = request.POST.get('term')
        year = request.POST.get('year')

        if not all([class_id, subject_id, term, year]):
            messages.error(request, "Please select class, subject, term, and year.")
            return redirect('primary_dashboard:marks_select')

        try:
            selected_class = Class.objects.get(id=class_id)
            students = Student.objects.filter(current_class_id=class_id)
            subject = Subject.objects.get(id=subject_id)
        except (Class.DoesNotExist, Subject.DoesNotExist):
            messages.error(request, "Selected class or subject not found.")
            return redirect('primary_dashboard:marks_select')

        # Pre-fill existing marks
        marks = {}
        for student in students:
            mark_instance = Mark.objects.filter(student=student, subject=subject, term=term, year=year).first()
            marks[student.id] = mark_instance.score if mark_instance else ''

        context = {
            'students': students,
            'subject': subject,
            'term': term,
            'year': year,
            'selected_class': selected_class,
            'marks': marks,
        }
        return render(request, 'primary_dashboard/marks.html', context)

    # For GET request, redirect to the selection form
    return redirect('primary_dashboard:marks_select')

@login_required
def export_students_excel(request, class_id):
    """Export all students in a class to Excel."""
    from openpyxl import Workbook
    from django.http import HttpResponse

    class_obj = get_object_or_404(Class, id=class_id)
    students = Student.objects.filter(current_class=class_obj).select_related('parent')

    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = f"Class {class_obj.name}"

    # Header row
    headers = [
        'First Name', 'Middle Name', 'Last Name', 'Gender',
        'Date of Birth', 'Admission Date', 'Class',
        'Parent First Name', 'Parent Middle Name', 'Parent Last Name',
        'Parent Phone', 'Parent Email'
    ]
    ws.append(headers)

    # Data rows
    for student in students:
        row = [
            student.first_name,
            student.middle_name or '',
            student.last_name,
            student.get_gender_display(),
            student.date_of_birth.strftime('%Y-%m-%d') if student.date_of_birth else '',
            student.admission_date.strftime('%Y-%m-%d'),
            student.current_class.name,
            student.parent.first_name if student.parent else '',
            student.parent.middle_name if student.parent else '',
            student.parent.last_name if student.parent else '',
            student.parent.phone if student.parent else '',
            student.parent.email if student.parent else ''
        ]
        ws.append(row)

    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=students_class_{class_obj.name}.xlsx'
    wb.save(response)
    return response

@login_required
def export_class_reports_excel(request, class_id):
    """Export class reports to Excel with student names, marks, and grades sorted by performance."""
    from openpyxl import Workbook
    from django.http import HttpResponse
    from django.db.models import Sum, Avg

    class_obj = get_object_or_404(Class, id=class_id)
    term = request.GET.get('term', '')
    year = request.GET.get('year', '')

    students = Student.objects.filter(current_class=class_obj)

    # Get all subjects for the class
    subjects = class_obj.subjects.all()

    # Prepare data for each student
    student_data = []
    for student in students:
        marks = Mark.objects.filter(
            student=student, term=term, year=year
        ).select_related('subject', 'grade')

        total_score = marks.aggregate(total=Sum('score'))['total'] or 0
        average_score = marks.aggregate(avg=Avg('score'))['avg'] or 0

        # Get overall grade based on average
        overall_grade = Grade.objects.filter(min_score__lte=average_score, max_score__gte=average_score).first()

        student_info = {
            'name': f"{student.first_name} {student.last_name}",
            'total_score': total_score,
            'average_score': average_score,
            'grade': overall_grade.name if overall_grade else 'N/A',
            'marks': {mark.subject.name: mark.score for mark in marks}
        }
        student_data.append(student_info)

    # Sort by total score descending
    student_data.sort(key=lambda x: x['total_score'], reverse=True)

    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = f"Reports {class_obj.name} {term} {year}"

    # Header row
    headers = ['Name']
    for subject in subjects:
        headers.append(subject.name)
    headers.extend(['Total Score', 'Average Score', 'Grade'])
    ws.append(headers)

    # Data rows
    for data in student_data:
        row = [data['name']]
        for subject in subjects:
            score = data['marks'].get(subject.name, '')
            row.append(score)
        row.extend([data['total_score'], round(data['average_score'], 2), data['grade']])
        ws.append(row)

    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=reports_{class_obj.name}_{term}_{year}.xlsx'
    wb.save(response)
    return response


@login_required
def delete_all_students(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    if class_obj.class_teacher != request.user:
        messages.error(request, 'You are not authorized to delete students from this class.')
        return redirect('primary_dashboard:class_detail', class_id=class_id)

    student_count = Student.objects.filter(current_class=class_obj).count()

    if request.method == 'POST':
        Student.objects.filter(current_class=class_obj).delete()
        messages.success(request, 'All students in the class have been deleted successfully!')
        return redirect('primary_dashboard:class_detail', class_id=class_id)
    else:
        context = {
            'class_obj': class_obj,
            'student_count': student_count,
        }
        return render(request, 'primary_dashboard/delete_all_students.html', context)

@login_required
def documents_list(request):
    from secondary_dashboard.models import DocumentUpload
    documents = DocumentUpload.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    return render(request, 'primary_dashboard/documents.html', {'documents': documents})

@login_required
def upload_document(request):
    from .forms import DocumentUploadForm
    from secondary_dashboard.models import DocumentUpload
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        # Primary uploads do not target a specific teacher — they are intended for parents (is_active=True)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            # No target_teacher for primary uploads; keep document visible to parents via is_active=True
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('primary_dashboard:documents')
    else:
        form = DocumentUploadForm()

    return render(request, 'primary_dashboard/upload_document.html', {'form': form})

@login_required
def delete_document(request, doc_id):
    from secondary_dashboard.models import DocumentUpload
    document = get_object_or_404(DocumentUpload, id=doc_id, uploaded_by=request.user)
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return redirect('primary_dashboard:documents')
    return render(request, 'primary_dashboard/delete_document.html', {'document': document})
