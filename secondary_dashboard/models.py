from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid



# =============================================================================
# CORE SCHOOL STRUCTURE MODELS
# =============================================================================

class SchoolSettings(models.Model):
    """Stores school-wide settings like name, logo, and contact information."""
    name = models.CharField(max_length=255, default="School Name")
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)
    school_motto = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    current_term = models.CharField(max_length=20, blank=True, help_text="e.g., Term 1, Semester 2")
    current_year = models.PositiveIntegerField(blank=True, null=True, help_text="e.g., 2024")

    def __str__(self):
        return self.name or "School Settings"

class Stream(models.Model):
    """Represents a stream within a form, e.g., North, South."""
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class Subject(models.Model):
    """Represents a subject taught in the school."""
    SUBJECT_CATEGORIES = [
        ('CORE', 'Core Subject'),
        ('SCIENCE', 'Science Options'),
        ('ARTS', 'Arts Options'),
        ('TECH', 'Technical Subjects'),
        ('LANG', 'Languages'),
    ]
    
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, unique=True)
    category = models.CharField(max_length=10, choices=SUBJECT_CATEGORIES, default='CORE')
    is_elective = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class StudentClass(models.Model):
    """
    Represents a form in the school, e.g., Form 1 North.
    This model defines the different forms (e.g., Form 1, Form 2) and their streams.
    """
    CLASS_LEVELS = [(str(i), f"Form {i}") for i in range(1, 7)]
    
    name = models.CharField(max_length=10, choices=CLASS_LEVELS, help_text="The form level, e.g., Form 1")
    stream = models.ForeignKey(Stream, on_delete=models.SET_NULL, null=True, blank=True, help_text="The stream, e.g., North, South")
    class_teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="class_teacher_of")
    subjects = models.ManyToManyField(Subject, blank=True)
    
    class Meta:
        verbose_name = "Form"
        verbose_name_plural = "Forms"
        unique_together = ('name', 'stream')
    
    def __str__(self):
        stream_name = f" {self.stream.name}" if self.stream else ""
        return f"{self.get_name_display()}{stream_name}"

class Grade(models.Model):
    """Represents the grading scheme, e.g. A, B, C."""
    name = models.CharField(max_length=20)
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    grade_point = models.DecimalField(max_digits=3, decimal_places=1)
    remarks = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.min_score}-{self.max_score}) - {self.grade_point} points"

class ExamDivision(models.Model):
    """Represents the final exam divisions, e.g., Division I, II."""
    DIVISION_CHOICES = [
        ('1', 'Division I'),
        ('2', 'Division II'),
        ('3', 'Division III'),
        ('4', 'Division IV'),
        ('0', 'Failed'),
    ]
    
    name = models.CharField(max_length=1, choices=DIVISION_CHOICES, unique=True)
    min_points = models.IntegerField()
    max_points = models.IntegerField()
    description = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['min_points']
    
    def __str__(self):
        return f"{self.get_name_display()} ({self.min_points}-{self.max_points} points)"

# =============================================================================
# PEOPLE MODELS
# =============================================================================

class Parent(models.Model):
    """Represents a parent or guardian of a student."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='parent_profile')
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, unique=True) # Phone should be unique
    email = models.EmailField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Student(models.Model):
    """Represents a student."""
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    
    student_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    admission_date = models.DateField(auto_now_add=True)
    student_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, related_name="students")
    parent = models.ForeignKey(Parent, on_delete=models.SET_NULL, null=True, related_name='children')
    profile_pic = models.ImageField(upload_to='student_profiles/', null=True, blank=True)
    medical_info = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.student_id:
            # Generate a unique student ID, e.g., S- followed by a short unique ID
            self.student_id = f"S-{str(uuid.uuid4().hex)[:8].upper()}"
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        """Return the full name of the student."""
        return f"{self.first_name} {self.last_name}"
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

# =============================================================================
# ACADEMIC RECORDS MODELS
# =============================================================================

class Mark(models.Model):
    """Stores marks for each student, subject, and assessment."""
    ASSESSMENT_TYPES = [
        ('CAT1', 'Continuous Assessment Test 1'),
        ('CAT2', 'Continuous Assessment Test 2'),
        ('EXAM', 'End of Term Exam'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.CharField(max_length=20)
    year = models.CharField(max_length=4)
    assessment_type = models.CharField(max_length=4, choices=ASSESSMENT_TYPES, default='EXAM')
    score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'subject', 'term', 'year', 'assessment_type')
    
    def __str__(self):
        return f"{self.student} - {self.subject} ({self.assessment_type}): {self.score}"

class Report(models.Model):
    """Stores generated reports for each student per term."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='reports')
    term = models.CharField(max_length=20)
    year = models.CharField(max_length=4)
    total_points = models.IntegerField(default=0)
    division = models.ForeignKey(ExamDivision, on_delete=models.SET_NULL, null=True, blank=True)
    overall_position = models.IntegerField(null=True, blank=True)
    stream_position = models.IntegerField(null=True, blank=True)
    class_teacher_comment = models.TextField(blank=True)
    principal_comment = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'term', 'year')

    def save(self, *args, **kwargs):
        if self.total_points is not None:
            self.division = ExamDivision.objects.filter(
                min_points__lte=self.total_points,
                max_points__gte=self.total_points
            ).first()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Report for {self.student} ({self.term} {self.year}) - {self.division}"



# =============================================================================
# COMMUNICATION MODELS
# =============================================================================

class Message(models.Model):
    """Model for sending messages between staff and parents."""
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='secondary_sent_messages')
    recipient = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='secondary_received_messages')
    subject = models.CharField(max_length=100)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.recipient} - {self.subject}"
    

class TeacherSignature(models.Model):
    teacher = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    signature_image = models.ImageField(upload_to='signatures/')

    def __str__(self):
        return f"Signature for {self.teacher.username}"

class Division(models.Model):
    """Represents a grading division based on total points."""
    name = models.CharField(max_length=50, unique=True)
    min_points = models.IntegerField()
    max_points = models.IntegerField()

    class Meta:
        ordering = ['min_points']

    def __str__(self):
        return f"{self.name} ({self.min_points}-{self.max_points} points)"

# =============================================================================
# EVENT MODEL
# =============================================================================

class Event(models.Model):
    EVENT_TYPES = [
        ('graduation', 'Graduation'),
        ('meeting', 'Parent-Teacher Meeting'),
        ('sports', 'Sports Event'),
        ('cultural', 'Cultural Event'),
        ('exam', 'Exam Related'),
        ('holiday', 'Holiday/Closure'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='secondary_events')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Timetable(models.Model):
    # Support forms 1..7 (include Form 7 for primary schools that have Class 7)
    FORM_CHOICES = [(str(i), f"Form {i}") for i in range(1, 8)]
    form = models.CharField(max_length=1, choices=FORM_CHOICES)
    file = models.FileField(upload_to='timetables/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='secondary_timetables')

    def __str__(self):
        return f"Timetable for {self.get_form_display()}"


# Notifications model for secondary dashboard (stored separately for local use)
class Notification(models.Model):
    TARGET_CHOICES = [
        ('all_teachers', 'All Teachers'),
        ('by_class', 'Specific Class'),
    ]

    title = models.CharField(max_length=255)
    message = models.TextField()
    target_type = models.CharField(max_length=20, choices=TARGET_CHOICES, default='all_teachers')
    target_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='secondary_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    # Track which users have read this notification so we can show unread counts/badges
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='secondary_notifications_read')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_target_type_display()})"

class DocumentUpload(models.Model):
    DOCUMENT_TYPES = [
        ('mock_exam', 'Mock Exam Results'),
        ('joint_exam', 'Joint Exam Results'),
        ('national_exam', 'National Exam Results'),
        ('joining_instructions', 'Joining Instructions'),
        ('other', 'Other Documents'),
    ]

    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='other')
    file = models.FileField(upload_to='exam_documents/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    # Optionally associate the uploaded document with a specific teacher
    target_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='target_documents'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.get_document_type_display()}: {self.title}"

