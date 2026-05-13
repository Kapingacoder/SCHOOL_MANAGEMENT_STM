from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import Teacher
from django.core.exceptions import ValidationError
from django.utils import timezone


class TeacherLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    school_level = forms.ChoiceField(choices=[('primary', 'Primary School'), ('secondary', 'Secondary School')])


class TeacherRegistrationForm(UserCreationForm):
    """
    Custom registration form for teachers that extends Django's UserCreationForm
    Includes only the specified fields: Username, First Name, Last Name, Email,
    TSC Number, Phone, Password, Confirm Password, and Profile Picture
    """

    class Meta:
        model = Teacher  # Uses our custom Teacher model
        fields = [  # Only the 9 specified fields
            'username', 'email', 'first_name', 'last_name',
            'tsc_number', 'phone_number', 'profile_picture'
        ]
    
    def clean_date_of_birth(self):
        """Validate that teacher is at least 18 years old"""
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            age = (timezone.now().date() - dob).days // 365
            if age < 18:
                raise ValidationError("You must be at least 18 years old.")
        return dob
    
    def clean_tsc_number(self):
        """Validate that TSC number is unique"""
        tsc_number = self.cleaned_data.get('tsc_number')
        if Teacher.objects.filter(tsc_number=tsc_number).exists():
            raise ValidationError("This TSC number is already registered.")
        return tsc_number


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Custom password change form with enhanced validation and user experience
    """
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password',
            'autocomplete': 'current-password'
        })
    )

    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your new password',
            'autocomplete': 'new-password'
        }),
        help_text="""
        <ul>
            <li>Your password must be at least 8 characters long</li>
            <li>Include at least one uppercase letter (A-Z)</li>
            <li>Include at least one lowercase letter (a-z)</li>
            <li>Include at least one number (0-9)</li>
            <li>Include at least one special character (!@#$%^&*)</li>
        </ul>
        """
    )

    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your new password',
            'autocomplete': 'new-password'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom styling to all fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'autocomplete': 'new-password' if 'new' in field_name else 'current-password'
                })
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def clean_old_password(self):
        """Validate that the old password is correct"""
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError("Your current password is incorrect.")
        return old_password

    def clean_new_password1(self):
        """Enhanced password validation"""
        password = self.cleaned_data.get('new_password1')

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        if not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase letter.")

        if not any(char.islower() for char in password):
            raise ValidationError("Password must contain at least one lowercase letter.")

        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one number.")

        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
            raise ValidationError("Password must contain at least one special character.")

        # Check if password is not too similar to old password
        old_password = self.cleaned_data.get('old_password', '')
        if old_password and len(password) <= len(old_password) + 2:
            # Check for character similarity
            common_chars = set(old_password.lower()) & set(password.lower())
            if len(common_chars) >= len(old_password) * 0.7:  # 70% similarity
                raise ValidationError("New password is too similar to your old password.")

        return password

    def clean(self):
        """Ensure new passwords match"""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise ValidationError("The new passwords do not match.")

        return cleaned_data
