from .models import Class
from django.contrib.auth import get_user_model

User = get_user_model()

def classes_context(request):
    classes = Class.objects.all()
    return {'classes': classes}

def teacher_context(request):
    teachers = User.objects.filter(groups__name='Teachers')
    total_teachers = teachers.count()
    return {
        'teachers': teachers,
        'total_teachers': total_teachers
    }


def unread_notifications(request):
    """Provide unread notification counts (primary + secondary) for the current user.

    Returns:
      {'unread_notifications': int, 'primary_unread': int, 'secondary_unread': int}
    """
    if not request.user.is_authenticated:
        return {'unread_notifications': 0, 'primary_unread': 0, 'secondary_unread': 0}

    try:
        from .models import Notification as PrimaryNotification
        from secondary_dashboard.models import Notification as SecondaryNotification

        primary_unread = PrimaryNotification.objects.filter(is_active=True).exclude(read_by=request.user).count()
        secondary_unread = SecondaryNotification.objects.filter(is_active=True).exclude(read_by=request.user).count()
        total = primary_unread + secondary_unread
    except Exception:
        primary_unread = 0
        secondary_unread = 0
        total = 0

    return {
        'unread_notifications': total,
        'primary_unread': primary_unread,
        'secondary_unread': secondary_unread,
    }