from django import forms
from primary_dashboard.models import Event
from .models import Student, Subject, Grade, SchoolSettings, Division, Message, Parent, DocumentUpload

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

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'middle_name', 'last_name', 'gender', 'date_of_birth', 'student_class', 'parent', 'profile_pic', 'medical_info']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'medical_info': forms.Textarea(attrs={'rows': 3}),
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'category', 'is_elective']

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['name', 'min_score', 'max_score', 'grade_point', 'remarks']

class SchoolSettingsForm(forms.ModelForm):
    class Meta:
        model = SchoolSettings
        fields = ['name', 'logo', 'school_motto', 'address', 'phone_number', 'email', 'current_term', 'current_year']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class DivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = ['name', 'min_points', 'max_points']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = DocumentUpload
        fields = ['title', 'document_type', 'file', 'description', 'target_teacher']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class StudentModalForm(forms.Form):
    """Lightweight modal form for quick student addition.

    Collects student basic info, selects the student's form, allows an optional
    profile picture upload, and captures parent name/phone/email to create a
    Parent if one isn't selected.
    """
    first_name = forms.CharField(max_length=50)
    middle_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50)
    gender = forms.ChoiceField(choices=Student.GENDER_CHOICES)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    student_class = forms.ModelChoiceField(queryset=Student._meta.get_field('student_class').remote_field.model.objects.all())
    profile_pic = forms.ImageField(required=False)

    # Parent quick fields (for creating a new Parent)
    parent_first_name = forms.CharField(max_length=50)
    parent_middle_name = forms.CharField(max_length=50, required=False)
    parent_last_name = forms.CharField(max_length=50)
    parent_phone = forms.CharField(max_length=15)
    parent_email = forms.EmailField(required=False)
