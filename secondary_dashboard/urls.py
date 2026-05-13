from django.urls import path, include
from . import views

app_name = 'secondary_dashboard'

urlpatterns = [
    # =========================================================================
    # CORE & DASHBOARD URLS
    # =========================================================================
    # Dashboard homepage
    path('home/', views.HomeView.as_view(), name='home'),
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('events/', views.events_list, name='events_list'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('events/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    # School settings page
    path('settings/', views.SettingsView.as_view(), name='settings'),

    # =========================================================================
    # STUDENT & CLASS MANAGEMENT URLS
    # =========================================================================
    # View students by form
    path('forms/<int:class_id>/', views.ClassManagementView.as_view(), name='class_management'),
    # Export students in a form to Excel
    path('forms/<int:class_id>/export/', views.export_students_excel, name='export_students_excel'),
    # Add a new student
    path('student/add/', views.StudentCreateView.as_view(), name='add_student'),
    # Edit an existing student's details
    path('student/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='edit_student'),
    # Delete a student from the records
    path('student/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='delete_student'),

    # =========================================================================
    # SUBJECT MANAGEMENT URLS
    # =========================================================================
    # List all subjects
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    # Add a new subject
    path('subject/add/', views.SubjectCreateView.as_view(), name='add_subject'),
    # Edit an existing subject
    path('subject/<int:pk>/edit/', views.SubjectUpdateView.as_view(), name='edit_subject'),
    # Delete a subject
    path('subject/<int:pk>/delete/', views.SubjectDeleteView.as_view(), name='delete_subject'),

    # =========================================================================
    # GRADE MANAGEMENT URLS
    # =========================================================================
    # List all grading schemes
    path('grades/', views.GradeListView.as_view(), name='grade_list'),
    # Add a new grade
    path('grade/add/', views.GradeCreateView.as_view(), name='add_grade'),
    # Edit an existing grade
    path('grade/<int:pk>/edit/', views.GradeUpdateView.as_view(), name='edit_grade'),
    # Delete a grade
    path('grade/<int:pk>/delete/', views.GradeDeleteView.as_view(), name='delete_grade'),

    # =========================================================================
    # DIVISION MANAGEMENT URLS
    # =========================================================================
    # Edit an existing division
    path('division/<int:pk>/edit/', views.DivisionUpdateView.as_view(), name='edit_division'),
    # Delete a division
    path('division/<int:pk>/delete/', views.DivisionDeleteView.as_view(), name='delete_division'),

    # =========================================================================
    # MARKS & REPORTING URLS
    # =========================================================================
    # Page to select class/subject for entering marks
    path('marks/select/', views.MarksSelectView.as_view(), name='marks_select'),
     # Page for entering marks for students
    path('marks/entry/<int:class_id>/', views.MarksEntryView.as_view(), name='marks_entry'),
    # Page to select class/student for viewing reports
   # Page to select class/student for viewing reports
    path('reports/select/', views.ReportSelectView.as_view(), name='report_select'),
    # View a single student's report
    path('reports/view/<int:class_id>/', views.ReportView.as_view(), name='report_view'),
    # View a specific student's report for parents
    path('reports/student/<int:student_id>/', views.StudentReportView.as_view(), name='student_report_view'),
    # Save comments for a student's report
    path('reports/save-comments/<int:student_id>/', views.save_report_comments, name='save_report_comments'),
    # Generate a PDF for a single report
    path('reports/pdf/<int:pk>/', views.ReportPdfView.as_view(), name='report_pdf'),
    # Export class reports to Excel
    path('reports/export-excel/<int:class_id>/', views.export_class_reports_excel, name='export_class_reports_excel'),
    # View/Print all reports for a class
    path('reports/print-all/', views.PrintAllReportsView.as_view(), name='print_all_reports'),
    path('report',views.report,name='report'),

    # =========================================================================


    # =========================================================================
    # MESSAGING URLS
    # =========================================================================
    # Page for sending/viewing messages
    path('messages/', views.MessageView.as_view(), name='messages'),
    path('forms/', views.FormListView.as_view(), name='form_list'),
    path('teachers/', views.TeacherListView.as_view(), name='teacher_list'),

    # =========================================================================
    # PASSWORD CHANGE URLS
    # =========================================================================
    # Password change functionality
    path('change_password/', include('accounts.urls')),
    path('timetable/', views.timetable_view, name='timetable'),
    # Past Papers Section
    path('past-papers/', views.PastPaperView.as_view(), name='past_papers'),
    path('past-papers/download/', views.PastPaperDownloadView.as_view(), name='download_past_paper'),
    path('embedded-content/', views.EmbeddedContentView.as_view(), name='embedded_content'),
    path('how-to-use/', views.HowToUseView.as_view(), name='how_to_use'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('documents/', views.DocumentListView.as_view(), name='documents'),
    path('documents/upload/', views.DocumentUploadView.as_view(), name='upload_document'),
    path('documents/delete/<int:pk>/', views.DocumentDeleteView.as_view(), name='delete_document'),
]