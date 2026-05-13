from django.contrib import admin
from .models import (
    SchoolSettings, Stream, Subject, StudentClass, Grade, ExamDivision,
    Parent, Student, Mark, Report, Message
)

from .models import Notification, Timetable

# Customizing the admin interface for a better user experience

@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_term', 'current_year')
    fieldsets = (
        (None, {
            'fields': ('name', 'logo', 'address', 'phone_number', 'email')
        }),
        ('Academic Details', {
            'fields': ('current_term', 'current_year')
        }),
    )

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'is_elective')
    list_filter = ('category', 'is_elective')
    search_fields = ('name', 'code')

@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'class_teacher')
    list_filter = ('name', 'stream')
    search_fields = ('name', 'stream__name', 'class_teacher__username')
    filter_horizontal = ('subjects',)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_score', 'max_score', 'grade_point')
    ordering = ('-min_score',)
    search_fields = ('name',)  # Hii ndiyo laini iliyoongezwa

@admin.register(ExamDivision)
class ExamDivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_points', 'max_points', 'description')
    ordering = ('min_points',)

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'email', 'get_username')
    search_fields = ('first_name', 'last_name', 'phone', 'email')

    def get_username(self, obj):
        return obj.user.username if obj.user else ''
    get_username.short_description = 'Username'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'student_class', 'gender')
    list_filter = ('student_class', 'gender')
    search_fields = ('student_id', 'first_name', 'last_name', 'parent__first_name', 'parent__last_name')
    readonly_fields = ('student_id', 'admission_date')

@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'assessment_type', 'score', 'term', 'year')
    list_filter = ('term', 'year', 'subject', 'assessment_type')
    search_fields = ('student__first_name', 'student__last_name', 'subject__name')
    autocomplete_fields = ('student', 'subject', 'grade')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('student', 'term', 'year', 'division', 'total_points')
    list_filter = ('term', 'year', 'division')
    search_fields = ('student__first_name', 'student__last_name')
    readonly_fields = ('date_created',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'recipient__first_name', 'subject')
    readonly_fields = ('timestamp',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'is_active')
    search_fields = ('title', 'message')


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('form', 'uploaded_by', 'uploaded_at')
    search_fields = ('form',)