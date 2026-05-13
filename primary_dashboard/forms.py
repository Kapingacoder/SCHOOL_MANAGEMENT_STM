from django import forms
from .models import Event, Class, Subject, Student, Grade, Mark, Report, Message, SchoolSettings, Parent
from secondary_dashboard.models import DocumentUpload

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location', 'event_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
        }

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'subjects']
        widgets = {
            'subjects': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            # If teacher is provided, we can add additional logic if needed
            pass

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'middle_name', 'last_name', 'gender', 'date_of_birth', 'current_class', 'parent']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['current_class'].queryset = Class.objects.filter(class_teacher=teacher)


class StudentModalForm(forms.Form):
    """A lightweight form used in the Add Student modal: collects student info
    plus plain parent name fields (no parent selection/current_class field).
    This is intended to post to the class_detail_view which assigns the class.
    """
    first_name = forms.CharField(max_length=50)
    middle_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50)
    gender = forms.ChoiceField(choices=Student.GENDER_CHOICES)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    parent_first_name = forms.CharField(max_length=50)
    parent_middle_name = forms.CharField(max_length=50, required=False)
    parent_last_name = forms.CharField(max_length=50)
    parent_phone = forms.CharField(max_length=15, required=False)
    parent_email = forms.EmailField(required=False)

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['name', 'min_score', 'max_score']

class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['student', 'subject', 'term', 'year', 'score', 'grade', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['student', 'term', 'year', 'comments', 'class_teacher_comment', 'headteacher_comment']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
            'class_teacher_comment': forms.Textarea(attrs={'rows': 3}),
            'headteacher_comment': forms.Textarea(attrs={'rows': 3}),
        }

class MessageForm(forms.Form):
    recipient = forms.ModelChoiceField(
        queryset=Parent.objects.all(),
        label="Recipient",
        empty_label="Select a parent",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

class MarksSelectForm(forms.Form):
    class_name = forms.ModelChoiceField(queryset=Class.objects.all(), empty_label="Select Class")
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(), empty_label="Select Subject")
    term = forms.ChoiceField(choices=[('Term 1', 'Term 1'), ('Term 2', 'Term 2'), ('Term 3', 'Term 3')])
    year = forms.CharField(max_length=4, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Year'}))

class ReportSelectForm(forms.Form):
    class_name = forms.ModelChoiceField(queryset=Class.objects.all(), empty_label="Select Class")
    term = forms.ChoiceField(choices=[('Term 1', 'Term 1'), ('Term 2', 'Term 2'), ('Term 3', 'Term 3')])
    year = forms.CharField(max_length=4, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Year'}))

class SchoolSettingsForm(forms.ModelForm):
    class Meta:
        model = SchoolSettings
        fields = ['name', 'logo', 'email', 'phone', 'address', 'school_motto', 'term', 'year']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = DocumentUpload
        fields = ['title', 'document_type', 'file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class TimetableUploadForm(forms.ModelForm):
    class Meta:
        from secondary_dashboard.models import Timetable
        model = Timetable
        fields = ['form', 'file']
        widgets = {
            'form': forms.Select(attrs={'class': 'form-select'}),
        }


class NotificationForm(forms.ModelForm):
    class Meta:
        from .models import Notification
        model = Notification
        fields = ['title', 'message', 'target_type', 'target_class']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'target_type': forms.Select(attrs={'class': 'form-select'}),
            'target_class': forms.Select(attrs={'class': 'form-select'}),
        }
