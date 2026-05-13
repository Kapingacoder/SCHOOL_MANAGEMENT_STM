# EVENTS FEATURE
from django.contrib.auth.decorators import login_required
@login_required
def events_list(request):
    from primary_dashboard.models import Event
    events = Event.objects.all().order_by('-date')
    return render(request, 'secondary_dashboard/events.html', {'events': events})

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
            return redirect('secondary_dashboard:events_list')
    else:
        form = EventForm()
    return render(request, 'secondary_dashboard/create_event.html', {'form': form})

@login_required
def edit_event(request, event_id):
    from primary_dashboard.models import Event
    from .forms import EventForm
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('secondary_dashboard:events_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'secondary_dashboard/edit_event.html', {'form': form, 'event': event})

@login_required
def delete_event(request, event_id):
    from primary_dashboard.models import Event
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('secondary_dashboard:events_list')
    return render(request, 'secondary_dashboard/delete_event.html', {'event': event})
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# Save comments for a student's report
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import redirect

@require_POST
def save_report_comments(request, student_id):
    """Save class teacher and principal comments for a student's report."""
    from .models import Report, Student, SchoolSettings
    student = get_object_or_404(Student, pk=student_id)
    settings = SchoolSettings.objects.first()
    term = settings.current_term if settings else ''
    year = settings.current_year if settings else ''
    report, created = Report.objects.get_or_create(student=student, term=term, year=year)
    report.class_teacher_comment = request.POST.get('class_teacher_comment', '')
    report.principal_comment = request.POST.get('principal_comment', '')
    report.save()
    messages.success(request, 'Comments saved successfully!')
    # Redirect back to the report view for the same class
    return redirect('secondary_dashboard:report_view', class_id=student.student_class.id)
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    TemplateView, CreateView, UpdateView, DeleteView, ListView, View
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Count

# Import models and forms from the current app
from .models import (
    Student, Parent, StudentClass, Subject, Grade, Mark, Report,
    SchoolSettings, Stream, Message, TeacherSignature, Division,ExamDivision, DocumentUpload
)
from . import forms
from django.db.models import Sum, Avg, Count, Q
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
try:
    from weasyprint import HTML, CSS
except Exception:
    # weasyprint is optional for PDF generation; if it's not installed, disable PDF features gracefully
    HTML = None
    CSS = None
from django.conf import settings
from decimal import Decimal
import os
from accounts.models import Teacher



# ... existing code ...
from django.utils import timezone
from primary_dashboard.models import Event

from datetime import datetime, timedelta

class HomeView(LoginRequiredMixin, TemplateView):
    """Displays the main dashboard with summary statistics."""
    template_name = 'secondary_dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        student_count = Student.objects.count()
        teacher_count = Teacher.objects.filter(school_level='secondary').count()
        class_count = StudentClass.objects.count()
        
        # Get upcoming events
        upcoming_events = Event.objects.filter(date__gte=timezone.now()).order_by('date')

        # Get recent activities (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_students = Student.objects.filter(admission_date__gte=seven_days_ago)
        recent_events = Event.objects.filter(date__gte=seven_days_ago)

        recent_activities = []
        for student in recent_students:
            recent_activities.append({
                'description': f'New student registered: {student.first_name} {student.last_name}',
                'timestamp': student.admission_date
            })
        for event in recent_events:
            recent_activities.append({
                'description': f'New event created: {event.title}',
                'timestamp': event.date
            })

        # Sort activities by timestamp
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)

        # Performance summary (average marks per class)
        class_performance = []
        classes = StudentClass.objects.all()
        for cls in classes:
            avg_marks = Mark.objects.filter(student__student_class=cls).aggregate(Avg('score'))['score__avg']
            class_performance.append({
                'class_name': cls.name,
                'average_marks': avg_marks or 0
            })

        context.update({
            'student_count': student_count,
            'teacher_count': teacher_count,
            'class_count': class_count,
            'upcoming_events': upcoming_events,
            'recent_activities': recent_activities,
            'class_performance': class_performance,
        })
        return context

# =============================================================================
# DASHBOARD & COSRE VIEWS
# =============================================================================
class DashboardView(LoginRequiredMixin, TemplateView):
# ... existing code ...

    """Displays the main dashboard with summary statistics."""
    template_name = 'secondary_dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Always fetch teachers and their count
        secondary_teachers = Teacher.objects.filter(school_level='secondary')
        total_teachers = secondary_teachers.count()

        # Filter students and parents based on form selection
        form_id = self.request.GET.get('form_id')
        selected_form = None
        
        if form_id:
            try:
                selected_form = StudentClass.objects.get(id=form_id)
                students = Student.objects.filter(student_class=selected_form)
                # Get parents of students in the selected form
                total_parents = Parent.objects.filter(children__in=students).distinct().count()
            except StudentClass.DoesNotExist:
                students = Student.objects.none()
                total_parents = 0
        else:
            students = Student.objects.all()
            total_parents = Parent.objects.count()

        total_students = students.count()

        context.update({
            'total_students': total_students,
            'total_parents': total_parents,
            'total_teachers': total_teachers,
            'forms': StudentClass.objects.all(),
            'selected_form_id': form_id,
            'selected_form': selected_form,
            'secondary_teachers': secondary_teachers,
        })
        return context
class SettingsView(LoginRequiredMixin, TemplateView):
    """Allows updating of school-wide settings, subjects, and grades."""
    template_name = 'secondary_dashboard/settings.html'
    success_url = reverse_lazy('secondary_dashboard:settings')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings_obj, _ = SchoolSettings.objects.get_or_create(pk=1)

        # Initialize forms
        context['form'] = kwargs.get('form', forms.SchoolSettingsForm(instance=settings_obj))
        context['subject_form'] = kwargs.get('subject_form', forms.SubjectForm())
        context['grade_form'] = kwargs.get('grade_form', forms.GradeForm())
        context['division_form'] = kwargs.get('division_form', forms.DivisionForm())

        # Provide existing data for listing
        context['subjects'] = Subject.objects.all()
        context['grades'] = Grade.objects.all()
        context['divisions'] = Division.objects.all()
        
        return context

    def post(self, request, *args, **kwargs):
        settings_obj, _ = SchoolSettings.objects.get_or_create(pk=1)
        context_to_render = {}

        # Handle settings form submission
        if 'settings_submit' in request.POST:
            settings_form = forms.SchoolSettingsForm(request.POST, request.FILES, instance=settings_obj)
            if settings_form.is_valid():
                settings_form.save()
                return redirect(self.success_url)
            else:
                context_to_render['form'] = settings_form

        # Handle subject form submission
        elif 'subject_submit' in request.POST:
            subject_form = forms.SubjectForm(request.POST)
            if subject_form.is_valid():
                subject_form.save()
                return redirect(self.success_url)
            else:
                context_to_render['subject_form'] = subject_form

        # Handle grade form submission
        elif 'grade_submit' in request.POST:
            grade_form = forms.GradeForm(request.POST)
            if grade_form.is_valid():
                grade_form.save()
                return redirect(self.success_url)
            else:
                context_to_render['grade_form'] = grade_form

        # Handle division form submission
        elif 'division_submit' in request.POST:
            division_form = forms.DivisionForm(request.POST)
            if division_form.is_valid():
                division_form.save()
                return redirect(self.success_url)
            else:
                context_to_render['division_form'] = division_form

class FormListView(LoginRequiredMixin, ListView):
    """Displays a list of all forms (classes)."""
    model = StudentClass
    template_name = 'secondary_dashboard/form_list.html'
    context_object_name = 'forms'

class TeacherListView(LoginRequiredMixin, ListView):
    """Displays a list of all secondary school teachers."""
    model = Teacher
    template_name = 'secondary_dashboard/teacher_list.html'
    context_object_name = 'teachers'

    def get_queryset(self):
        return Teacher.objects.filter(school_level='secondary')

        return self.render_to_response(self.get_context_data(**context_to_render))

# =============================================================================
# STUDENT & CLASS MANAGEMENT
# =============================================================================

class ClassManagementView(LoginRequiredMixin, TemplateView):
    """Handles listing students by form and adding new students."""
    template_name = 'secondary_dashboard/class_management.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_id = self.kwargs.get('class_id')
        context['forms'] = StudentClass.objects.order_by('name', 'stream')
        
        if form_id:
            selected_form = get_object_or_404(StudentClass, id=form_id)
            context['selected_form'] = selected_form
            context['students'] = Student.objects.filter(student_class=selected_form)
        else:
            first_form = StudentClass.objects.order_by('name', 'stream').first()
            if first_form:
                context['selected_form'] = first_form
                context['students'] = Student.objects.filter(student_class=first_form)
            else:
                context['selected_form'] = None
                context['students'] = Student.objects.none()
        
        # For the Add Student modal we use a lightweight modal form that collects
        # parent first/middle/last name and an optional profile picture.
        try:
            context['form'] = forms.StudentModalForm()
        except Exception:
            # Fallback to the regular StudentForm if the modal form is unavailable
            context['form'] = forms.StudentForm()
        return context

class StudentCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new student."""
    model = Student
    form_class = forms.StudentForm
    template_name = 'secondary_dashboard/edit_student.html'

    def get_success_url(self):
        # Redirect to the form list for the form the student was added to
        return reverse_lazy('secondary_dashboard:class_management', kwargs={'class_id': self.object.student_class.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add New Student'
        return context

    def post(self, request, *args, **kwargs):
        """Support two submission patterns:
        - Standard StudentForm (full form page)
        - Modal quick form which posts parent_first_name/... fields (StudentModalForm)
        """
        # If the modal sent parent_first_name, handle quick-create flow
        if 'parent_first_name' in request.POST:
            modal = forms.StudentModalForm(request.POST, request.FILES)
            if modal.is_valid():
                # Create Parent record
                first_name = modal.cleaned_data.get('parent_first_name', '')
                middle_name = modal.cleaned_data.get('parent_middle_name', '')
                last_name = modal.cleaned_data.get('parent_last_name', '')

                # Concatenate names for username, filtering out empty parts
                name_parts = [name for name in [first_name, middle_name, last_name] if name]
                base_username = '.'.join(name_parts).lower() or 'parent'

                # Ensure username is unique
                from django.contrib.auth import get_user_model
                User = get_user_model()
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}.{counter}"
                    counter += 1

                # Create a user for the parent
                parent_user = User.objects.create(username=username)
                parent_user.set_unusable_password()
                parent_user.save()

                parent = Parent.objects.create(
                    user=parent_user,
                    first_name=first_name,
                    middle_name=middle_name or '',
                    last_name=last_name,
                    phone=modal.cleaned_data.get('parent_phone'),
                    email=modal.cleaned_data.get('parent_email') or ''
                )

                # Create Student
                student = Student(
                    first_name=modal.cleaned_data.get('first_name'),
                    middle_name=modal.cleaned_data.get('middle_name') or '',
                    last_name=modal.cleaned_data.get('last_name'),
                    gender=modal.cleaned_data.get('gender'),
                    date_of_birth=modal.cleaned_data.get('date_of_birth'),
                    student_class=modal.cleaned_data.get('student_class'),
                    parent=parent
                )
                # Handle optional profile_pic
                pic = request.FILES.get('profile_pic')
                if pic:
                    student.profile_pic = pic
                student.save()
                return redirect(reverse_lazy('secondary_dashboard:class_management', kwargs={'class_id': student.student_class.id}))
            else:
                # Render the class management page with modal errors
                class_id = request.POST.get('student_class') or None
                if class_id:
                    return redirect(reverse('secondary_dashboard:class_management', kwargs={'class_id': class_id}))
                return redirect('secondary_dashboard:class_management')

        # Otherwise fall back to default CreateView behavior
        return super().post(request, *args, **kwargs)

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    """View for editing an existing student's details."""
    model = Student
    form_class = forms.StudentForm
    template_name = 'secondary_dashboard/edit_student.html'

    def get_success_url(self):
        return reverse_lazy('secondary_dashboard:class_management', kwargs={'class_id': self.object.student_class.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Student Details'
        return context

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    """View to confirm and handle the deletion of a student."""
    model = Student
    template_name = 'secondary_dashboard/delete_student.html'
    
    def get_success_url(self):
        if self.object.student_class:
            return reverse_lazy('secondary_dashboard:class_management', kwargs={'class_id': self.object.student_class.id})
        return reverse_lazy('secondary_dashboard:dashboard')

# =============================================================================
# SUBJECT & GRADE MANAGEMENT (CRUD Views)
# =============================================================================

class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = 'secondary_dashboard/subjects.html'
    context_object_name = 'subjects'

class SubjectCreateView(LoginRequiredMixin, CreateView):
    model = Subject
    form_class = forms.SubjectForm
    template_name = 'secondary_dashboard/edit_subject.html'
    success_url = reverse_lazy('secondary_dashboard:subject_list')

class SubjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Subject
    form_class = forms.SubjectForm
    template_name = 'secondary_dashboard/edit_subject.html'
    success_url = reverse_lazy('secondary_dashboard:subject_list')

class SubjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Subject
    template_name = 'secondary_dashboard/delete_subject.html'
    success_url = reverse_lazy('secondary_dashboard:subject_list')

class GradeListView(LoginRequiredMixin, ListView):
    model = Grade
    template_name = 'secondary_dashboard/grades.html'
    context_object_name = 'grades'

class GradeCreateView(LoginRequiredMixin, CreateView):
    model = Grade
    form_class = forms.GradeForm
    template_name = 'secondary_dashboard/edit_grade.html'
    success_url = reverse_lazy('secondary_dashboard:grade_list')

class GradeUpdateView(LoginRequiredMixin, UpdateView):
    model = Grade
    form_class = forms.GradeForm
    template_name = 'secondary_dashboard/edit_grade.html'
    success_url = reverse_lazy('secondary_dashboard:grade_list')

class GradeDeleteView(LoginRequiredMixin, DeleteView):
    model = Grade
    template_name = 'secondary_dashboard/delete_grade.html'
    success_url = reverse_lazy('secondary_dashboard:settings')

class DivisionUpdateView(LoginRequiredMixin, UpdateView):
    model = Division
    form_class = forms.DivisionForm
    template_name = 'secondary_dashboard/edit_division.html'
    success_url = reverse_lazy('secondary_dashboard:settings')

class DivisionDeleteView(LoginRequiredMixin, DeleteView):
    model = Division
    template_name = 'secondary_dashboard/delete_division.html'
    success_url = reverse_lazy('secondary_dashboard:settings')

# =============================================================================
# MARKS & REPORTING (Complex views - may need more logic)
# =============================================================================

class MarksSelectView(LoginRequiredMixin, TemplateView):
    """Page for selecting form and subject to enter marks."""
    template_name = 'secondary_dashboard/marks_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forms'] = StudentClass.objects.all()
        context['subjects'] = Subject.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        form_id = request.POST.get('form')
        subject_id = request.POST.get('subject')
        if form_id and subject_id:
            return redirect(reverse("secondary_dashboard:marks_entry", kwargs={"class_id": form_id}) + f'?subject={subject_id}')
        return self.get(request, *args, **kwargs)

class MarksEntryView(LoginRequiredMixin, TemplateView):
    """Page for entering marks for a list of students."""
    template_name = 'secondary_dashboard/marks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get('class_id')
        # Use request.GET to allow selecting subject from a dropdown/form
        subject_id = self.request.GET.get('subject')
        
        student_class = get_object_or_404(StudentClass, pk=class_id)
        subject = get_object_or_404(Subject, pk=subject_id)
        
        # Get current term and year from school settings
        settings = SchoolSettings.objects.first()
        term = settings.current_term if settings else ''
        year = str(settings.current_year) if settings and settings.current_year else ''

        students = Student.objects.filter(student_class=student_class).order_by('first_name', 'last_name')
        
        marks_data = []
        for student in students:
            # Fetch the existing mark for this student, subject, term, and year
            mark = Mark.objects.filter(
                student=student, 
                subject=subject, 
                term=term, 
                year=year
            ).first()
            marks_data.append({'student': student, 'mark': mark})

        context.update({
            'student_class': student_class,
            'subject': subject,
            'marks_data': marks_data,
            'term': term,
            'year': year,
        })
        return context

    def post(self, request, *args, **kwargs):
        class_id = self.kwargs.get('class_id')
        subject_id = request.GET.get('subject')
        
        subject = get_object_or_404(Subject, pk=subject_id)
        students = Student.objects.filter(student_class_id=class_id)
        
        settings = SchoolSettings.objects.first()
        term = settings.current_term if settings else ''
        year = str(settings.current_year) if settings and settings.current_year else ''

        for student in students:
            score_key = f'score_{student.id}'
            score_val = request.POST.get(score_key)
            
            if score_val:
                try:
                    score = int(score_val)
                    # Ensure score is within the valid 0-100 range
                    if 0 <= score <= 100:
                        # **CRITICAL FIX**: Find the corresponding grade for the score
                        grade = Grade.objects.filter(min_score__lte=score, max_score__gte=score).first()
                        
                        # Update or create the mark, now correctly including the grade
                        Mark.objects.update_or_create(
                            student=student,
                            subject=subject,
                            term=term,
                            year=year,
                            defaults={'score': score, 'grade': grade}
                        )
                except (ValueError, TypeError):
                    # Ignore if the input is not a valid number
                    continue
        
        # Redirect to the same page to show the newly entered marks
        return redirect(request.get_full_path())

class ReportSelectView(LoginRequiredMixin, TemplateView):
    """Page for selecting a form to view/print reports."""
    template_name = 'secondary_dashboard/report_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forms'] = StudentClass.objects.all()
        context['subjects'] = Subject.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        form_id = request.POST.get('form_id')
        if form_id:
            return redirect('secondary_dashboard:report_view', class_id=form_id)
        return self.get(request, *args, **kwargs)


class ReportView(LoginRequiredMixin, TemplateView):
    """
    Displays a detailed report for all students in a selected class,
    including scores, grades, ranks, and division.
    """
    template_name = 'secondary_dashboard/report_view.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get('class_id')
        student_class = get_object_or_404(StudentClass, pk=class_id)
        
        settings = SchoolSettings.objects.first()
        term = self.request.GET.get('term', settings.current_term if settings else '')
        year = self.request.GET.get('year', str(settings.current_year) if settings and settings.current_year else '')
        search_query = self.request.GET.get('search', '').strip()
        students = Student.objects.filter(student_class=student_class)
        
        # Apply search filter if search query exists
        if search_query:
            students = students.filter(
                Q(first_name__icontains=search_query) | 
                Q(last_name__icontains=search_query) |
                Q(student_id__icontains=search_query)
            )
        reports_data = []
        for student in students:
            marks = Mark.objects.filter(
                student=student, term=term, year=year
            ).select_related('grade', 'subject')
            
            # Initialize default values for students without marks
            total_score = 0
            average_score = 0
            total_points = 0
            division = "N/A"
            
            if marks.exists():
                total_score = marks.aggregate(total=Sum('score'))['total'] or 0
                average_score = marks.aggregate(avg=Avg('score'))['avg'] or 0
                
                # Only calculate points and division if we have marks
                sorted_marks = sorted(
                    marks, 
                    key=lambda m: m.grade.grade_point if m.grade and m.grade.grade_point is not None else Decimal('0.0'), 
                    reverse=True
                )
                
                top_seven_marks = sorted_marks[:7]
                total_points = sum(
                    mark.grade.grade_point for mark in top_seven_marks if mark.grade
                )
                
                division_obj = ExamDivision.objects.filter(
                    min_points__lte=total_points,
                    max_points__gte=total_points
                ).first()
                
                if division_obj:
                    division = division_obj.get_name_display()
            
            reports_data.append({
                'student': student,
                'marks': marks,
                'total_score': total_score,
                'average_score': average_score,
                'total_points': total_points,
                'division': division,
                'report': Report.objects.filter(student=student, term=term, year=year).first(),
            })
        # Rank students based on total score
        reports_data.sort(key=lambda x: x['total_score'], reverse=True)
        
        current_rank = 0
        last_score = -1
        for i, data in enumerate(reports_data):
            if data['total_score'] != last_score:
                current_rank = i + 1
                last_score = data['total_score']
            data['rank'] = current_rank
        context.update({
            'student_class': student_class,
            'reports_data': reports_data,
            'term': term,
            'year': year,
            'total_students_in_class': students.count(),
            'search_query': search_query,
        })
        return context

def report(request):
    return redirect('secondary_dashboard:report' )


class PrintAllReportsView(LoginRequiredMixin, TemplateView):
    """Displays a printable page of all reports for a selected form."""
    template_name = 'secondary_dashboard/print_all_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.request.GET.get('class_id')
        if class_id:
            student_class = get_object_or_404(StudentClass, id=class_id)
            students = Student.objects.filter(student_class=student_class)
            school_settings = SchoolSettings.objects.first()

            reports_data = []
            for student in students:
                marks = Mark.objects.filter(student=student)
                total_score = sum(mark.score for mark in marks if mark.score is not None)
                subject_count = marks.count()
                average_score = total_score / subject_count if subject_count > 0 else 0

                reports_data.append({
                    'student': student,
                    'marks': marks,
                    'total_score': total_score,
                    'average_score': average_score,
                })

            context['reports_data'] = reports_data
            context['class_obj'] = student_class
            context['term'] = school_settings.current_term if school_settings else ''
            context['year'] = school_settings.current_year if school_settings else ''
            
        return context

class StudentReportView(LoginRequiredMixin, TemplateView):
    """Displays a detailed report for a specific student."""
    template_name = 'secondary_dashboard/parent_report_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = self.kwargs.get('student_id')
        student = get_object_or_404(Student, pk=student_id)

        settings = SchoolSettings.objects.first()
        term = self.request.GET.get('term', settings.current_term if settings else '')
        year = self.request.GET.get('year', settings.current_year if settings else '')

        marks = Mark.objects.filter(
            student=student, term=term, year=year
        ).select_related('grade', 'subject')

        # Calculate total score and average from raw scores
        total_score = marks.aggregate(total=Sum('score'))['total'] or 0
        average_score = marks.aggregate(avg=Avg('score'))['avg'] or 0

        # --- Logic to calculate division based on best 7 subjects ---
        # 1. Sort marks by grade points (descending). Handle None for grade/grade_point.
        sorted_marks = sorted(
            marks,
            key=lambda m: m.grade.grade_point if m.grade and m.grade.grade_point is not None else Decimal('0.0'),
            reverse=True
        )

        # 2. Get the top 7 marks
        top_seven_marks = sorted_marks[:7]

        # 3. Sum the grade points from these top 7 marks
        total_points = sum(
            mark.grade.grade_point for mark in top_seven_marks if mark.grade
        )

        # 4. Find the corresponding division - use ExamDivision instead of Division
        division_obj = ExamDivision.objects.filter(
            min_points__lte=total_points,
            max_points__gte=total_points
        ).first()

        division = division_obj.get_name_display() if division_obj else "N/A"
        # --- End of division logic ---

        # Calculate student rank in class
        all_students_in_class = Student.objects.filter(student_class=student.student_class)
        student_points = {}
        for s in all_students_in_class:
            s_marks = Mark.objects.filter(student=s, term=term, year=year).select_related('grade')
            s_sorted_marks = sorted(
                s_marks,
                key=lambda m: m.grade.grade_point if m.grade and m.grade.grade_point is not None else Decimal('0.0'),
                reverse=True
            )
            s_top_seven = s_sorted_marks[:7]
            s_total_points = sum(mark.grade.grade_point for mark in s_top_seven if mark.grade)
            student_points[s.id] = s_total_points

        sorted_students = sorted(student_points.items(), key=lambda item: item[1], reverse=True)

        student_rank = -1
        for i, (s_id, points) in enumerate(sorted_students):
            if s_id == student.id:
                student_rank = i + 1
                break

        context.update({
            'student': student,
            'marks': marks,
            'total_score': total_score,
            'average_score': average_score,
            'total_points': total_points,
            'division': division,
            'rank': student_rank,
            'total_students_in_class': all_students_in_class.count(),
            'term': term,
            'year': year,
            'report': Report.objects.filter(student=student, term=term, year=year).first(),
        })
        return context

class ReportPdfView(LoginRequiredMixin, View):
    """Generates a PDF version of a student's report."""

    def get(self, request, *args, **kwargs):
        student_id = self.kwargs.get('pk')
        student = get_object_or_404(Student, pk=student_id)

        school_settings = SchoolSettings.objects.first()
        term = school_settings.current_term if school_settings else ''
        year = str(school_settings.current_year) if school_settings and school_settings.current_year else ''

        marks = Mark.objects.filter(student=student, term=term, year=year).select_related('subject', 'grade')

        total_score = sum(mark.score for mark in marks if mark.score is not None)
        average_score = total_score / marks.count() if marks.exists() else 0

        valid_marks = sorted([m for m in marks if m.grade], key=lambda m: m.grade.grade_point)
        top_seven_marks = valid_marks[:7]
        total_points = sum(mark.grade.grade_point for mark in top_seven_marks)

        division_obj = ExamDivision.objects.filter(
            min_points__lte=total_points,
            max_points__gte=total_points
        ).first()
        division = division_obj.get_name_display() if division_obj else "N/A"

        all_students_in_class = Student.objects.filter(student_class=student.student_class)
        student_points = {}
        for s in all_students_in_class:
            s_marks = Mark.objects.filter(student=s, term=term, year=year).select_related('grade')
            s_valid_marks = sorted([m for m in s_marks if m.grade], key=lambda m: m.grade.grade_point)
            s_top_seven = s_valid_marks[:7]
            s_total_points = sum(mark.grade.grade_point for mark in s_top_seven)
            student_points[s.id] = s_total_points

        sorted_students = sorted(student_points.items(), key=lambda item: item[1])

        student_rank = -1
        for i, (s_id, points) in enumerate(sorted_students):
            if s_id == student.id:
                student_rank = i + 1
                break

        class_teacher_comment = request.GET.get('class_teacher_comment', '')
        principal_comment = request.GET.get('principal_comment', '')

        context = {
            'student': student,
            'marks': marks,
            'total_score': total_score,
            'average_score': average_score,
            'total_points': total_points,
            'division': division,
            'term': term,
            'year': year,
            'school_settings': school_settings,
            'teacher_signature': TeacherSignature.objects.first(),
            'overall_position': student_rank,
            'total_students': all_students_in_class.count(),
            'class_teacher_comment': class_teacher_comment,
            'principal_comment': principal_comment,
        }

        html_string = render_to_string('secondary_dashboard/report_pdf.html', context)

        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{student.first_name}_{student.last_name}_report.pdf"'

        return response
# =============================================================================
# PARENT PORTAL & MESSAGING (Placeholders)
# =============================================================================

def parent_login(request):
    # This view is now deprecated, parent login is handled in accounts app
    return redirect('accounts:parent_login')

def parent_dashboard(request):
    # This view is now deprecated, parent dashboard is handled in accounts app
    return redirect('accounts:parent_dashboard')

class MessageView(LoginRequiredMixin, CreateView):
    """Handles sending messages to parents."""
    model = Message
    form_class = forms.MessageForm
    template_name = 'secondary_dashboard/message.html'
    success_url = reverse_lazy('secondary_dashboard:messages')

    def form_valid(self, form):
        subject = form.cleaned_data.get('subject')
        message_text = form.cleaned_data['message']
        parents = Parent.objects.all()
        for parent in parents:
            Message.objects.create(
                sender=self.request.user,
                recipient=parent,
                subject=subject,
                message=message_text,
                is_delivered=True
            )
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get messages sent by this teacher
        context['sent_messages'] = Message.objects.filter(sender=self.request.user).order_by('-timestamp')
        return context

@login_required
def export_students_excel(request, class_id):
    """Export all students in a form to Excel."""
    from openpyxl import Workbook
    from django.http import HttpResponse

    student_class = get_object_or_404(StudentClass, id=class_id)
    students = Student.objects.filter(student_class=student_class).select_related('parent')

    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = f"Form {student_class.get_name_display()}"

    # Header row
    headers = [
        'Student ID', 'First Name', 'Middle Name', 'Last Name', 'Gender',
        'Date of Birth', 'Admission Date', 'Form', 'Stream',
        'Parent First Name', 'Parent Middle Name', 'Parent Last Name',
        'Parent Phone', 'Parent Email', 'Parent Occupation', 'Medical Info'
    ]
    ws.append(headers)

    # Data rows
    for student in students:
        row = [
            student.student_id,
            student.first_name,
            student.middle_name or '',
            student.last_name,
            student.get_gender_display(),
            student.date_of_birth.strftime('%Y-%m-%d') if student.date_of_birth else '',
            student.admission_date.strftime('%Y-%m-%d'),
            student.student_class.get_name_display(),
            student.student_class.stream.name if student.student_class.stream else '',
            student.parent.first_name if student.parent else '',
            student.parent.middle_name if student.parent else '',
            student.parent.last_name if student.parent else '',
            student.parent.phone if student.parent else '',
            student.parent.email if student.parent else '',
            student.parent.occupation if student.parent else '',
            student.medical_info or ''
        ]
        ws.append(row)

    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=students_form_{student_class.get_name_display()}.xlsx'
    wb.save(response)
    return response

@login_required
def export_class_reports_excel(request, class_id):
    """Export class reports to Excel with student names, marks, and grades sorted by performance."""
    from openpyxl import Workbook
    from django.http import HttpResponse
    from django.db.models import Sum, Avg

    student_class = get_object_or_404(StudentClass, id=class_id)
    term = request.GET.get('term', '')
    year = request.GET.get('year', '')

    students = Student.objects.filter(student_class=student_class)

    # Get all subjects that have marks for students in this class, term, and year
    subjects = Subject.objects.filter(
        mark__student__in=students,
        mark__term=term,
        mark__year=year
    ).distinct()

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
    ws.title = f"Reports {student_class.get_name_display()} {term} {year}"

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
    response['Content-Disposition'] = f'attachment; filename=reports_{student_class.get_name_display()}_{term}_{year}.xlsx'
    wb.save(response)
    return response

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from .models import Timetable as SecondaryTimetable, Notification as SecondaryNotification
from django.db.models import Q
import requests
from urllib.parse import urlparse
import os

def _is_admin(user):
    """Return True if the user should be considered an admin for dashboard actions."""
    try:
        return user.is_staff or user.is_superuser or user.groups.filter(name__in=['Admin', 'Administrators']).exists()
    except Exception:
        return user.is_staff or user.is_superuser


@login_required
def timetable_view(request):
    """Show timetables and allow admins to upload per-form timetables (Forms 1-6)."""
    # Handle upload (admin only)
    if request.method == 'POST':
        if not _is_admin(request.user):
            messages.error(request, 'You do not have permission to upload timetables.')
            return redirect('secondary_dashboard:timetable')

        form_choice = request.POST.get('form')
        uploaded_file = request.FILES.get('file')
        if form_choice and uploaded_file:
            tt = SecondaryTimetable(form=form_choice, file=uploaded_file, uploaded_by=request.user)
            tt.save()
            messages.success(request, 'Timetable uploaded successfully.')
            return redirect('secondary_dashboard:timetable')
        else:
            messages.error(request, 'Please select a form and a file to upload.')
            return redirect('secondary_dashboard:timetable')

    # GET: gather timetables per form (1..6)
    forms_data = []
    for i in range(1, 7):
        form_num = str(i)
        q = SecondaryTimetable.objects.filter(form=form_num).order_by('-uploaded_at')
        forms_data.append({'num': form_num, 'timetables': q})

    # Determine teacher forms if applicable
    teacher_forms = set()
    try:
        teacher_classes = StudentClass.objects.filter(class_teacher=request.user).values_list('name', flat=True)
        teacher_forms = set(teacher_classes)
    except Exception:
        teacher_forms = set()

    return render(request, 'secondary_dashboard/timetable.html', {
        'forms_data': forms_data,
        'teacher_forms': teacher_forms,
        'is_admin': _is_admin(request.user),
    })

class PastPaperDownloadView(LoginRequiredMixin, View):
    """View to handle downloading past papers."""
    
    def get(self, request, *args, **kwargs):
        url = request.GET.get('url')
        if not url:
            return HttpResponseBadRequest("URL parameter is required")
        
        try:
            # Get the filename from URL or use a default one
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path) or 'past_paper.pdf'
            
            # Stream the file from the source URL
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Create a response with the file
            response = HttpResponse(
                response.content,
                content_type=response.headers.get('Content-Type', 'application/octet-stream')
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except requests.RequestException as e:
            return HttpResponseServerError(f"Error downloading file: {str(e)}")
        except Exception as e:
            return HttpResponseServerError(f"An error occurred: {str(e)}")


class PastPaperView(LoginRequiredMixin, TemplateView):
    template_name = 'secondary_dashboard/past_paper.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = [
            {
                'name': 'Comprehensive Collections',
                'sources': [
                    {
                        'name': 'Maktaba TZ',
                        'url': 'https://maktaba.tetea.org/resources/',
                        'description': 'Official past papers from TETEA',
                        'icon': 'book',
                        'color': 'primary'
                    },
                    {
                        'name': 'Waza Elimu',
                        'url': 'https://wazaelimu.com/past-papers-form-1-4-midterm-terminal-annual-joint-exams/',
                        'description': 'Form 1-4 past papers (Midterm, Terminal, Annual)',
                        'icon': 'file-alt',
                        'color': 'success'
                    },
                    {
                        'name': 'Learning Hub Tanzania',
                        'url': 'https://learninghubtz.co.tz/secondary-exams-series.php',
                        'description': 'Organized by subject and form',
                        'icon': 'graduation-cap',
                        'color': 'info'
                    },
                ]
            },
            {
                'name': 'Subject-Specific Papers',
                'sources': [
                    {
                        'name': 'Mathematics Papers',
                        'url': 'https://www.scribd.com/document/659168987/Mathematics-Form-One-Terminal',
                        'description': 'Form 1-4 Mathematics past papers',
                        'icon': 'square-root-alt',
                        'color': 'danger'
                    },
                    {
                        'name': 'Science Papers',
                        'url': 'https://www.elimu-resource.com/secondary-past-papers/physics/',
                        'description': 'Physics, Chemistry, Biology',
                        'icon': 'flask',
                        'color': 'warning'
                    },
                    {
                        'name': 'Humanities',
                        'url': 'https://www.tzpastpapers.com/category/history/',
                        'description': 'History, Geography, Civics',
                        'icon': 'globe-africa',
                        'color': 'success'
                    }
                ]
            },
            {
                'name': 'Joint Exams',
                'sources': [
                    {
                        'name': 'National Exams',
                        'url': 'https://www.necta.go.tz/psle',
                        'description': 'Necta past papers',
                        'icon': 'file-certificate',
                        'color': 'dark'
                    },
                    {
                        'name': 'Joint Regional',
                        'url': 'https://pastpapershared.com/secondary_pastpapers.php',
                        'description': 'Regional joint examinations',
                        'icon': 'copy',
                        'color': 'secondary'
                    }
                ]
            }
        ]
        return context

class EmbeddedContentView(LoginRequiredMixin, TemplateView):
    template_name = 'secondary_dashboard/embedded_content.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url'] = self.request.GET.get('url', '')
        context['title'] = self.request.GET.get('title', 'Past Papers')
        return context

class HowToUseView(LoginRequiredMixin, TemplateView):
    template_name = 'secondary_dashboard/how_to_use.html'

@login_required
def notifications_view(request):
    """Notifications page for secondary dashboard.

    Admins can POST new notifications (these are saved in the primary Notification model
    so they are visible across dashboards). Teachers/others see notifications.
    """
    # Handle new notification (admin only)
    if request.method == 'POST':
        if not _is_admin(request.user):
            messages.error(request, 'You do not have permission to send notifications.')
            return redirect('secondary_dashboard:notifications')

        title = request.POST.get('title')
        message_text = request.POST.get('message')
        target_type = request.POST.get('target_type', 'all_teachers')
        # Save to secondary Notification model (local to this app)
        SecondaryNotification.objects.create(
            title=title or 'No title',
            message=message_text or '',
            target_type=target_type,
            created_by=request.user,
        )
        messages.success(request, 'Notification sent successfully.')
        return redirect('secondary_dashboard:notifications')

    # GET: show notifications (mix of real notifications and placeholders)
    # For now, fetch recent notifications from primary Notification model
    try:
        recent_qs = SecondaryNotification.objects.filter(is_active=True).order_by('-created_at')[:20]
        recent = list(recent_qs)
        # Build a simple notifications list for template (keeps existing structure)
        notifications = [{'title': n.title, 'message': n.message, 'is_new': (not n.read_by.filter(id=request.user.id).exists())} for n in recent]
        # Count unread
        unread_count = sum(1 for n in notifications if n.get('is_new'))
        # Mark them as read for this user (so badge updates on next request)
        try:
            unread_qs = recent_qs.exclude(read_by=request.user)
            for n in unread_qs:
                n.read_by.add(request.user)
        except Exception:
            pass
    except Exception:
        notifications = [
            {'title': 'Welcome!', 'message': 'Karibu kwenye mfumo wa dashboard ya sekondari.', 'is_new': True},
            {'title': 'Exam Timetable', 'message': 'Ratiba ya mitihani ya mwisho wa muhula imeongezwa.', 'is_new': True},
        ]
        unread_count = sum(1 for n in notifications if n.get('is_new'))

    return render(request, 'secondary_dashboard/notifications.html', {
        'notifications': notifications,
        'unread_notifications': unread_count,
        'is_admin': _is_admin(request.user),
    })

class DocumentListView(LoginRequiredMixin, ListView):
    model = DocumentUpload
    template_name = 'secondary_dashboard/documents.html'
    context_object_name = 'documents'

    def get_queryset(self):
        return DocumentUpload.objects.filter(is_active=True)

class DocumentUploadView(LoginRequiredMixin, CreateView):
    model = DocumentUpload
    form_class = forms.DocumentUploadForm
    template_name = 'secondary_dashboard/upload_document.html'
    success_url = reverse_lazy('secondary_dashboard:documents')

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = DocumentUpload
    template_name = 'secondary_dashboard/delete_document.html'
    success_url = reverse_lazy('secondary_dashboard:documents')
