from django.db import models
from django.contrib.auth.models import AbstractUser  # Extends Django's default User model
from django.core.validators import RegexValidator  # For validating fields like phone numbers

class Teacher(AbstractUser):
    """
    Custom Teacher model that extends Django's AbstractUser
    Includes all default User fields plus additional teacher-specific fields
    """
    
    # Gender choices constant
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    SCHOOL_LEVEL_CHOICES = [
    ('primary', 'Primary School'),
    ('secondary', 'Secondary School'),
]
    
    # Validator for Tanzanian phone numbers (+255xxxxxxxxx)
    phone_regex = RegexValidator(
        regex=r'^\+?255\d{9}$',
        message="Phone number must be entered in the format: '+255xxxxxxxxx'."
    )
    
    # Teacher Service Commission number (unique for each teacher)
    tsc_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="TSC Number",
        null=True,
        blank=True
    )
    
    # Gender field with predefined choices
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )
    
    # Date of birth field
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Phone number field with Tanzanian validation
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=13,
        null=True,
        blank=True
    )
    
   # Professional information fields
    qualification = models.CharField(max_length=100, null=True, blank=True)  # Highest academic qualification
    subjects_taught = models.CharField(max_length=200, null=True, blank=True)  # Subjects separated by commas
    current_school = models.CharField(max_length=150, null=True, blank=True)  # Current school name
    school_level = models.CharField(
        max_length=10,
        choices=SCHOOL_LEVEL_CHOICES,
        null=True,
        blank=True
    )
    district = models.CharField(max_length=100, null=True, blank=True)  # District of the school
    region = models.CharField(max_length=100, null=True, blank=True)  # Region of the school
    
    # Optional profile picture
    profile_picture = models.ImageField(
        upload_to='teacher_profiles/',  # Files will be uploaded to MEDIA_ROOT/teacher_profiles/
        blank=True,
        null=True
    )
    
    # Automatic registration date
    registration_date = models.DateTimeField(auto_now_add=True)
    
    # Verification status (defaults to False)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Teacher"  # Singular name in admin
        verbose_name_plural = "Teachers"  # Plural name in admin

    def __str__(self):
        """String representation of the Teacher model"""
        return f"{self.get_full_name()} ({self.tsc_number})"