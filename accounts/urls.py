from django.urls import path
from django.contrib.auth import views as auth_views
from .views import teacher_register, teacher_login, teacher_logout, parent_login, parent_dashboard, CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView, delete_message, change_password, change_password_done, parent_change_password, parent_change_password_done, primary_change_password, primary_change_password_done, secondary_change_password, secondary_change_password_done

app_name = 'accounts'

urlpatterns = [
    path('register/', teacher_register, name='teacher_register'),
    path('login/', teacher_login, name='teacher_login'),
    path('logout/', teacher_logout, name='teacher_logout'),  # Added logout URL
    path('parent/login/', parent_login, name='parent_login'),
    path('parent/dashboard/', parent_dashboard, name='parent_dashboard'),

    # Password reset URLs
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Password change URLs
    path('change_password/', change_password, name='change_password'),
    path('change_password/done/', change_password_done, name='change_password_done'),

    # Specific password change URLs for different user types
    path('parent_change_password/', parent_change_password, name='parent_change_password'),
    path('parent_change_password/done/', parent_change_password_done, name='parent_change_password_done'),
    path('primary_dashboard_change_password/', primary_change_password, name='primary_dashboard_change_password'),
    path('primary_dashboard_change_password/done/', primary_change_password_done, name='primary_dashboard_change_password_done'),
    path('secondary_dashboard_change_password/', secondary_change_password, name='secondary_dashboard_change_password'),
    path('secondary_dashboard_change_password/done/', secondary_change_password_done, name='secondary_dashboard_change_password_done'),

    # Message management
    path('message/delete/<int:message_id>/<str:school_type>/', delete_message, name='delete_message'),
]
