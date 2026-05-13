from django.contrib import admin
from .models import (
    SchoolSettings, Class, Student, Subject, Grade, Report, Message, Parent, Mark,
    Notification, Timetable
)

@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email')

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_teacher')
    list_filter = ('class_teacher',)
    search_fields = ('name', 'class_teacher__username')
    filter_horizontal = ('subjects',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['subjects'].required = False
        return form

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'current_class', 'gender', 'parent')
    list_filter = ('current_class', 'gender')
    search_fields = ('first_name', 'last_name', 'parent__first_name', 'parent__last_name')
    list_per_page = 20

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_score', 'max_score')

@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'term', 'year', 'score', 'grade')
    list_filter = ('term', 'year', 'subject', 'student__current_class')
    search_fields = ('student__first_name', 'student__last_name', 'subject__name')
    list_per_page = 25

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'term', 'year', 'date_created')
    list_filter = ('term', 'year', 'date_created')
    search_fields = ('student__first_name', 'student__last_name')

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'email', 'get_username')
    search_fields = ('first_name', 'last_name', 'email')

    def get_username(self, obj):
        return obj.user.username if obj.user else ''
    get_username.short_description = 'Username'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'recipient__first_name', 'recipient__last_name')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'is_active')
    search_fields = ('title', 'message')


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('title', 'form', 'uploaded_by', 'uploaded_at', 'is_active')
    search_fields = ('title',)