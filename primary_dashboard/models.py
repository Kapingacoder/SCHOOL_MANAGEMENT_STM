from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# School Event Model
class Event(models.Model):
    EVENT_TYPES = [
        ('graduation', 'Graduation'),
        ('meeting', 'Parent-Teacher Meeting'),
        ('sports', 'Sports Event'),
        ('cultural', 'Cultural Event'),
        ('exam', 'Exam Related'),
        ('holiday', 'Holiday/Closure'),
        ('Others', 'others'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class SchoolSettings(models.Model):
    name = models.CharField(max_length=100, default="Primary School")
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    school_motto = models.CharField(max_length=255, blank=True)
    term = models.CharField(max_length=20, blank=True, default="Term 1")
    year = models.CharField(max_length=4, blank=True, default="2025")

    def __str__(self):
        return self.name

class Subject(models.Model):

    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name

class Grade(models.Model):
    name = models.CharField(max_length=20)  # e.g., A, B, C
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    
    def __str__(self):
        return f"{self.name} ({self.min_score}-{self.max_score})"

class Class(models.Model):
    CLASS_CHOICES = [(str(i), f"Class {i}") for i in range(1, 8)]
    name = models.CharField(max_length=10, choices=CLASS_CHOICES, unique=True)
    class_teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    subjects = models.ManyToManyField(Subject)
    
    def __str__(self):
        return self.get_name_display()

class Parent(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent')
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    admission_date = models.DateField(auto_now_add=True)
    current_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True)
    parent = models.ForeignKey(Parent, on_delete=models.SET_NULL, null=True, related_name='children')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.current_class})"

class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.CharField(max_length=20)
    year = models.CharField(max_length=4)
    score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True)
    comments = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'subject', 'term', 'year')
    
    def __str__(self):
        return f"{self.student} - {self.subject} ({self.score})"

class Report(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='reports')
    term = models.CharField(max_length=20)
    year = models.CharField(max_length=4)
    comments = models.TextField(blank=True)
    class_teacher_comment = models.TextField(blank=True)
    headteacher_comment = models.TextField(blank=True)
    class_teacher_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    headteacher_signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'term', 'year')

    def __str__(self):
        return f"Report for {self.student} ({self.term} {self.year})"

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.recipient} at {self.timestamp}"


class Notification(models.Model):
    """Simple notification model for admin -> teachers communication.

    - admin can create notifications targeted to all teachers or a specific class
    - teachers will see notifications targeted to all or to classes they teach
    """
    TARGET_CHOICES = [
        ('all_teachers', 'All Teachers'),
        ('by_class', 'Specific Class'),
    ]

    title = models.CharField(max_length=255)
    message = models.TextField()
    target_type = models.CharField(max_length=20, choices=TARGET_CHOICES, default='all_teachers')
    target_class = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    # Track which users have read this notification so we can show unread counts/badges
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='primary_notifications_read')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_target_type_display()})"


# Timetable model for the primary dashboard (keeps primary timetables separate)
class Timetable(models.Model):
    FORM_CHOICES = [(str(i), f"Class {i}") for i in range(1, 8)]
    form = models.CharField(max_length=2, choices=FORM_CHOICES)
    file = models.FileField(upload_to='timetables/')
    title = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_timetables')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Primary Timetable for {self.get_form_display()} - {self.title or 'Untitled'}"
