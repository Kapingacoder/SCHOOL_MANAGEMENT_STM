from django.urls import path
from django.urls import include
from django.views.generic import TemplateView, RedirectView
from .views import (
    classes_view, dashboard, settings_view, parent_login, parent_dashboard,
    save_marks, class_detail_view, delete_class, edit_class, subjects_view,
    delete_subject, edit_subject, students_view, delete_student, edit_student,
    grades_view, delete_grade, edit_grade, marks_select_view, marks_entry_view,
    report_select, report_view, print_all_reports, message_view, delete_message,
    marks_view, get_subjects, student_report_view, student_report_pdf, get_grade_for_score,
    export_students_excel, export_class_reports_excel, delete_all_students,
    events_list, create_event, edit_event, delete_event,
    documents_list, upload_document, delete_document, home, teachers_view, timetable_view, notifications_view
)

app_name = 'primary_dashboard'

urlpatterns = [
    path('home/', home, name='home'),
    path('classes/', classes_view, name='classes'),
    path('dashboard/', dashboard, name='dashboard'),
    path('events/', events_list, name='events_list'),
    path('events/create/', create_event, name='create_event'),
    path('events/edit/<int:event_id>/', edit_event, name='edit_event'),
    path('events/delete/<int:event_id>/', delete_event, name='delete_event'),
    path('settings/', settings_view, name='settings'),

    path('save_marks/', save_marks, name='save_marks'),
    path('class/<int:class_id>/', class_detail_view, name='class_detail'),
    path('class/<int:class_id>/export/', export_students_excel, name='export_students_excel'),
    path('class/<int:class_id>/delete/', delete_class, name='delete_class'),
    path('class/<int:class_id>/edit/', edit_class, name='edit_class'),
    path('class/<int:class_id>/delete_all_students/', delete_all_students, name='delete_all_students'),
    path('subjects/', subjects_view, name='subjects'),
    path('subject/<int:subject_id>/delete/', delete_subject, name='delete_subject'),
    path('subject/<int:subject_id>/edit/', edit_subject, name='edit_subject'),
    # Redirect legacy /students/ URL to /classes/ so users land on the classes page
    path('students/', RedirectView.as_view(pattern_name='primary_dashboard:classes', permanent=False), name='students'),
    path('student/<int:student_id>/delete/', delete_student, name='delete_student'),
    path('student/<int:student_id>/edit/', edit_student, name='edit_student'),
    path('grades/', grades_view, name='grades'),
    path('grade/<int:grade_id>/delete/', delete_grade, name='delete_grade'),
    path('grade/<int:grade_id>/edit/', edit_grade, name='edit_grade'),
    path('marks/select/', marks_select_view, name='marks_select'),
    path('marks/entry/<int:class_id>/<int:subject_id>/<str:term>/<int:year>/', marks_entry_view, name='marks_entry'),
    path('report/student/<int:student_id>/<int:class_id>/<str:term>/<int:year>/', student_report_view, name='student_report'),
    path('report/student/<int:student_id>/<int:class_id>/<str:term>/<int:year>/pdf/', student_report_pdf, name='student_report_pdf'),
    path('report/select/', report_select, name='report_select'),
    path('report/view/<int:class_id>/<str:term>/<int:year>/', report_view, name='view_class_report'),
    path('report/export-excel/<int:class_id>/', export_class_reports_excel, name='export_class_reports_excel'),
    path('report/print_all/<int:class_id>/<str:term>/<int:year>/', print_all_reports, name='print_all_reports'),
    path('messages/', message_view, name='messages'),
    path('message/<int:message_id>/delete/', delete_message, name='delete_message'),
    path('marks/', marks_view, name='marks'),
    path('ajax/get-subjects/', get_subjects, name='get_subjects'),
    path('ajax/get-grade/', get_grade_for_score, name='get_grade_for_score'),

    # Password change functionality
    path('change_password/', include('accounts.urls')),

    # Placeholder templates for dashboard icons
    path('teachers/', teachers_view, name='teachers'),
    path('timetable/', timetable_view, name='timetable'),
    path('past_papers/', TemplateView.as_view(template_name='primary_dashboard/past_papers.html'), name='past_papers'),
    path('how_to_use/', TemplateView.as_view(template_name='primary_dashboard/how_to_use.html'), name='how_to_use'),
    path('notifications/', notifications_view, name='notifications'),
    path('documents/', documents_list, name='documents'),
    path('documents/upload/', upload_document, name='upload_document'),
    path('documents/delete/<int:doc_id>/', delete_document, name='delete_document'),
]



