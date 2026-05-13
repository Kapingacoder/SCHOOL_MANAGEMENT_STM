from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse
from .forms import TeacherRegistrationForm, TeacherLoginForm
from .models import Teacher
from django.contrib import messages
from django.contrib.auth import get_user_model
from primary_dashboard.models import Parent as PrimaryParent, Student as PrimaryStudent, Mark as PrimaryMark, Report as PrimaryReport, SchoolSettings as PrimarySettings
from secondary_dashboard.models import Parent as SecondaryParent, Student as SecondaryStudent, Mark as SecondaryMark, Report as SecondaryReport, SchoolSettings as SecondarySettings


from django.http import JsonResponse

def teacher_login(request):
    if request.method == 'POST':
        form = TeacherLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            school_level = form.cleaned_data['school_level']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)  # Log the user in first

                # Check if the user is a superuser
                if user.is_superuser:
                    messages.success(request, f'Welcome Admin, {user.username}!')
                    return redirect('/admin/')

                # Continue with the logic for regular teachers
                if hasattr(user, 'school_level') and user.school_level == school_level:
                    if school_level == 'primary':
                        return redirect('primary_dashboard:dashboard')
                    else:
                        return redirect('secondary_dashboard:dashboard')
                else:
                    # If the school level is incorrect, log the user out
                    logout(request)
                    messages.error(request, 'The selected school level is incorrect for your account.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    form = TeacherLoginForm()
    return render(request, 'accounts/teacher_login.html', {'form': form})

def parent_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        UserModel = get_user_model()
        parent_user = UserModel.objects.filter(username=username).first()
        if not parent_user:
            messages.error(request, "Username haipo. Hakikisha umeandika kama ilivyo kwenye database ya shule.")
            return render(request, 'accounts/parent_login.html')

        # Check if parent has usable password or is setting new password
        if not parent_user.has_usable_password() or (new_password and confirm_password):
            if not new_password or not confirm_password:
                messages.error(request, "Weka password mpya na uthibitishe.")
                return render(request, 'accounts/parent_login.html')
            if new_password != confirm_password:
                messages.error(request, "Password hazifanani.")
                return render(request, 'accounts/parent_login.html')
            parent_user.set_password(new_password)
            parent_user.save()
            messages.success(request, "Password imewekwa! Sasa unaweza ku-login.")
            user = authenticate(request, username=username, password=new_password)
            if user:
                login(request, user)
                return redirect('accounts:parent_dashboard')
            else:
                messages.error(request, "Tatizo kwenye ku-login. Jaribu tena.")
                return render(request, 'accounts/parent_login.html')
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('accounts:parent_dashboard')
            else:
                messages.error(request, "Username au password si sahihi.")
                return render(request, 'accounts/parent_login.html')
    return render(request, 'accounts/parent_login.html')

def parent_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('accounts:parent_login')

    UserModel = get_user_model()
    user = request.user

    # Try to get primary parent profile
    try:
        primary_parent = PrimaryParent.objects.get(user=user)
    except PrimaryParent.DoesNotExist:
        primary_parent = None

    # Try to get secondary parent profile
    try:
        secondary_parent = SecondaryParent.objects.get(user=user)
    except SecondaryParent.DoesNotExist:
        secondary_parent = None

    # Collect children from both primary and secondary
    children = []
    if primary_parent:
        children += list(PrimaryStudent.objects.filter(parent=primary_parent))
    if secondary_parent:
        children += list(SecondaryStudent.objects.filter(parent=secondary_parent))

    # Get current term and year from either primary or secondary settings
    primary_settings = PrimarySettings.objects.first()
    secondary_settings = SecondarySettings.objects.first()
    term = primary_settings.term if primary_settings else (secondary_settings.current_term if secondary_settings else '')
    year = primary_settings.year if primary_settings else (secondary_settings.current_year if secondary_settings else '')

    # Prepare reports for each child
    children_reports = []
    children_charts = []
    for child in children:
        if isinstance(child, PrimaryStudent):
            # Get all marks for the student (not filtered by term/year to show all results)
            marks = PrimaryMark.objects.filter(student=child)
            report = PrimaryReport.objects.filter(student=child, term=term, year=year).first() if term and year else None
            school_type = 'primary'
            class_id = child.current_class.id if child.current_class else None
        else:
            # Get all marks for the student (not filtered by term/year to show all results)
            marks = SecondaryMark.objects.filter(student=child)
            report = SecondaryReport.objects.filter(student=child, term=term, year=year).first() if term and year else None
            school_type = 'secondary'
            class_id = child.student_class.id if hasattr(child, 'student_class') and child.student_class else None
        children_reports.append({
            'child': child,
            'marks': marks,
            'report': report,
            'school_type': school_type,
            'class_id': class_id,
        })
        
        # Prepare chart data
        subject_names = [mark.subject.name for mark in marks if mark.score is not None]
        subject_scores = [mark.score for mark in marks if mark.score is not None]
        if subject_names and subject_scores:
            import json
            children_charts.append({
                'child_id': child.id,
                'child_name': f"{child.first_name} {child.last_name}",
                'subject_names': json.dumps(subject_names),
                'subject_scores': json.dumps(subject_scores),
                'school_type': school_type,
            })

    # Get messages sent to this parent from both primary and secondary
    received_messages = []
    if primary_parent:
        from primary_dashboard.models import Message as PrimaryMessage
        for msg in PrimaryMessage.objects.filter(recipient=primary_parent):
            received_messages.append({'message': msg, 'school_type': 'primary'})

    if secondary_parent:
        from secondary_dashboard.models import Message as SecondaryMessage
        for msg in SecondaryMessage.objects.filter(recipient=secondary_parent):
            received_messages.append({'message': msg, 'school_type': 'secondary'})

    # Sort messages by timestamp (most recent first)
    received_messages.sort(key=lambda x: x['message'].timestamp, reverse=True)

    # Count unread messages
    unread_count = sum(1 for item in received_messages if not item['message'].is_read)

    # Mark all messages as read when parent views the dashboard
    for item in received_messages:
        msg = item['message']
        if not msg.is_read:
            msg.is_read = True
            msg.save()

    # Get events from both primary and secondary dashboards
    from primary_dashboard.models import Event as PrimaryEvent
    from secondary_dashboard.models import Event as SecondaryEvent
    primary_events = PrimaryEvent.objects.all()
    secondary_events = SecondaryEvent.objects.all()
    # Combine and sort events by date descending
    all_events = list(primary_events) + list(secondary_events)
    all_events.sort(key=lambda x: x.date, reverse=True)

    # Get documents from secondary dashboard (assuming documents are uploaded there)
    from secondary_dashboard.models import DocumentUpload
    documents = DocumentUpload.objects.filter(is_active=True).order_by('-uploaded_at')

    context = {
        'children': children,
        'children_reports': children_reports,
        'children_charts': children_charts,
        'term': term,
        'year': year,
        'received_messages': received_messages,
        'unread_count': unread_count,
        'events': all_events,
        'documents': documents,
    }
    return render(request, 'accounts/base_parent_dashboard.html', context)

from django.contrib.auth.decorators import login_required
from primary_dashboard.models import Message as PrimaryMessage
from secondary_dashboard.models import Message as SecondaryMessage

@login_required
def delete_message(request, message_id, school_type):
    if school_type == 'primary':
        message = get_object_or_404(PrimaryMessage, id=message_id)
    else:
        message = get_object_or_404(SecondaryMessage, id=message_id)

    # Ensure the user deleting the message is the recipient
    if request.user == message.recipient.user:
        message.delete()
        messages.success(request, "Message deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this message.")

    return redirect('accounts:parent_dashboard')


def teacher_register(request):
    """
    Handles teacher registration:
    Handles teacher registration:
    - Shows empty form on GET request
    - Processes form data on POST request
    - Logs in user after successful registration
    """
    
    if request.method == 'POST':
        # Create form instance with submitted data and files
        form = TeacherRegistrationForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Save the new teacher
            user = form.save()

            # Log the user in
            login(request, user, backend='accounts.backends.TeacherBackend')
            
            # Success message
            messages.success(request, 'Registration successful!')
            
            # Redirect to login page
            return redirect('accounts:teacher_login')
        else:
            print(form.errors)  
    else:
        # Create empty form for GET request
        form = TeacherRegistrationForm()
    
    # Render the template with the form
    return render(request, 'accounts/teacher_register.html', {'form': form})

def teacher_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:teacher_login')

def primary_dashboard(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'teacher') or request.user.teacher.school_level != 'primary':
        return redirect('teacher_login')
    return redirect('primary_dashboard:dashboard')

def secondary_dashboard(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'teacher') or request.user.teacher.school_level != 'secondary':
        return redirect('teacher_login')
    return redirect('secondary_dashboard:dashboard')

from django.urls import reverse_lazy

from django.http import HttpResponseRedirect

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')

    def form_valid(self, form):
        # Remove the email existence check for security and functionality
        # Django's default behavior sends email regardless of email existence
        response = super().form_valid(form)
        # Fix DisallowedRedirect by returning HttpResponseRedirect with absolute URL
        return HttpResponseRedirect(self.get_success_url())

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CustomPasswordChangeForm


@login_required
def change_password(request):
    """
    View for changing user password with comprehensive validation and security
    """
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            # Save the new password
            user = form.save()
            # Update session to prevent logout
            update_session_auth_hash(request, user)
            # Success message
            messages.success(
                request,
                'Your password has been changed successfully! You can continue using the system with your new password.'
            )
            # Redirect to success page
            return redirect('accounts:change_password_done')
        else:
            # Form has errors, display them
            messages.error(request, 'Please correct the errors below.')
    else:
        # GET request - show empty form
        form = CustomPasswordChangeForm(user=request.user)

    context = {
        'form': form,
        'title': 'Change Password'
    }
    return render(request, 'accounts/change_password.html', context)


@login_required
def change_password_done(request):
    """
    Success page after password change
    """
    context = {
        'title': 'Password Changed Successfully'
    }
    return render(request, 'accounts/change_password_done.html', context)


# Specific change password views for different user types

@login_required
def parent_change_password(request):
    """
    Change password view specifically for parents
    """
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request,
                'Your password has been changed successfully! You can continue using the system with your new password.'
            )
            return redirect('accounts:parent_change_password_done')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    context = {
        'form': form,
        'title': 'Change Password',
        'user_type': 'parent',
        'back_url': 'accounts:parent_dashboard'
    }
    return render(request, 'accounts/parent_change_password.html', context)


@login_required
def parent_change_password_done(request):
    """
    Success page after parent password change
    """
    context = {
        'title': 'Password Changed Successfully',
        'user_type': 'parent',
        'back_url': 'accounts:parent_dashboard'
    }
    return render(request, 'accounts/parent_change_password_done.html', context)


@login_required
def primary_change_password(request):
    """
    Change password view specifically for primary school teachers
    """
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request,
                'Your password has been changed successfully! You can continue using the system with your new password.'
            )
            return redirect('accounts:primary_dashboard_change_password_done')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    context = {
        'form': form,
        'title': 'Change Password',
        'user_type': 'primary',
        'back_url': 'primary_dashboard:dashboard'
    }
    return render(request, 'accounts/primary_change_password.html', context)


@login_required
def primary_change_password_done(request):
    """
    Success page after primary teacher password change
    """
    context = {
        'title': 'Password Changed Successfully',
        'user_type': 'primary',
        'back_url': 'primary_dashboard:dashboard'
    }
    return render(request, 'accounts/primary_change_password_done.html', context)


@login_required
def secondary_change_password(request):
    """
    Change password view specifically for secondary school teachers
    """
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request,
                'Your password has been changed successfully! You can continue using the system with your new password.'
            )
            return redirect('accounts:secondary_dashboard_change_password_done')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    context = {
        'form': form,
        'title': 'Change Password',
        'user_type': 'secondary',
        'back_url': 'secondary_dashboard:dashboard'
    }
    return render(request, 'accounts/secondary_change_password.html', context)


@login_required
def secondary_change_password_done(request):
    """
    Success page after secondary teacher password change
    """
    context = {
        'title': 'Password Changed Successfully',
        'user_type': 'secondary',
        'back_url': 'secondary_dashboard:dashboard'
    }
    return render(request, 'accounts/secondary_change_password_done.html', context)
