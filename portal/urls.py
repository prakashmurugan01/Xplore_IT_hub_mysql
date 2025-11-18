from django.urls import path
from . import views
from . import api_views
from . import views_profile
from . import chatbot_api

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('choose/', views.choose, name='choose'),
    path('python-full-stack/', views.python_full_stack, name='python_full_stack'),
    path('courses/', views.courses_full, name='courses_full'),
    path('instructor/<slug:slug>/', views.instructor_profile, name='instructor_profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Role redirect / dashboards
    path('dashboard/', views.role_redirect, name='role_redirect'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # Alias URL for clarity: superadmin dashboard (keeps backward compatibility)
    path('superadmin-dashboard/', views.admin_dashboard, name='superadmin_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/dashboard/updates/', views.teacher_dashboard_updates, name='teacher_dashboard_updates'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student-dashboard/adv/', views.student_dashboard_adv, name='student_dashboard_adv'),
    path('course/add/', views.add_course, name='add_course'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/assignments/', views.course_assignments, name='course_assignments'),

    # Student-facing assignments
    path('student/assignments/', views.student_assignments, name='student_assignments'),
    path('student/assignments/<int:assignment_id>/', views.student_assignment_detail, name='student_assignment_detail'),

    # AI & Prediction
    path('student/prediction/', views.student_prediction, name='student_prediction'),
    path('superadmin/ai-insights/', views.admin_ai_insights, name='admin_ai_insights'),
    # Superadmin advanced modules (scaffolded)
    path('superadmin/students/', views.superadmin_student_management, name='superadmin_student_management'),
    path('superadmin/students/add/', views.superadmin_student_add, name='superadmin_student_add'),
    path('superadmin/students/<int:profile_id>/edit/', views.superadmin_student_edit, name='superadmin_student_edit'),
    path('superadmin/students/<int:profile_id>/delete/', views.superadmin_student_delete, name='superadmin_student_delete'),
    path('superadmin/financial/', views.superadmin_financial_overview, name='superadmin_financial_overview'),
    path('superadmin/attendance-live/', views.superadmin_attendance_live, name='superadmin_attendance_live'),
    path('superadmin/updates/', views.superadmin_updates, name='superadmin_updates'),
    path('superadmin/students/list/', views.superadmin_student_list, name='superadmin_student_list'),
    path('superadmin/staff/list/', views.superadmin_staff_list, name='superadmin_staff_list'),
    # Superadmin staff attendance (webcam / face attendance MVP)
    path('superadmin/staff-attendance/', views.superadmin_staff_attendance, name='superadmin_staff_attendance'),
    path('superadmin/staff-attendance/recognize/', views.superadmin_staff_attendance_recognize, name='superadmin_staff_attendance_recognize'),
    path('superadmin/staff-attendance/updates/', views.superadmin_staff_attendance_updates, name='superadmin_staff_attendance_updates'),
    path('superadmin/staff-attendance/marked/', views.staff_attendance_marked, name='staff_attendance_marked'),
    # Debug helpers (development only)
    path('debug/whoami/', views.debug_whoami, name='debug_whoami'),
    path('superadmin/lists/', views.superadmin_full_lists, name='superadmin_full_lists'),

    # Study materials & feedback
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('course/<int:course_id>/materials/', views.materials_list, name='materials_list'),
    path('course/<int:course_id>/materials/upload/', views.upload_material, name='upload_material'),
    path('course/<int:course_id>/materials/admin-upload/', views.admin_upload_material, name='admin_upload_material'),
    path('course/<int:course_id>/materials/manage/', views.teacher_manage_materials, name='manage_materials'),
    path('materials/download/<int:material_id>/', views.download_material, name='download_material'),
    path('materials/view/<int:material_id>/', views.view_material, name='view_material'),
    path('materials/delete/<int:material_id>/', views.delete_material, name='delete_material'),
    path('course/<int:course_id>/feedback/', views.submit_feedback, name='submit_feedback'),

    # API endpoints
    path('api/live-updates/', api_views.get_live_updates, name='get_live_updates'),
    path('api/analytics/', api_views.get_analytics, name='get_analytics'),
    path('api/student/tasks/', api_views.get_student_tasks, name='api_student_tasks'),
    path('api/student/materials/', api_views.get_student_materials, name='api_student_materials'),
    path('api/student/timetable/', api_views.get_student_timetable, name='api_student_timetable'),
    path('api/student/events/', api_views.get_student_events, name='api_student_events'),
    path('api/student/notifications/', api_views.get_student_notifications, name='api_student_notifications'),
    path('api/student/courses/', api_views.get_student_courses, name='api_student_courses'),
    path('api/student/attendance/', api_views.get_student_attendance, name='api_student_attendance'),
    path('api/attendance/realtime/', api_views.get_student_attendance, name='api_attendance_realtime'),
    path('api/latest-uploads/', api_views.get_latest_uploads, name='api_latest_uploads'),
    path('api/student/schedules/', api_views.get_student_schedules, name='api_student_schedules'),
    path('api/schedule-notifications/', api_views.get_schedule_notifications, name='api_schedule_notifications'),

    # Chatbot APIs
    path('api/chatbot/message/', chatbot_api.chatbot_message, name='chatbot_message'),
    path('api/chatbot/send-to-teacher/', chatbot_api.send_message_to_teacher, name='send_to_teacher'),
    path('api/chatbot/send-to-admin/', chatbot_api.send_message_to_admin, name='send_to_admin'),
    path('api/chatbot/teachers/', chatbot_api.get_teacher_list, name='get_teacher_list'),
        path('api/chatbot/admins/', chatbot_api.get_admin_list, name='get_admin_list'),
        path('api/chatbot/history/', chatbot_api.get_message_history, name='get_message_history'),

    # Attendance
    path('teacher/attendance/<int:course_id>/', views.take_attendance, name='take_attendance'),
    path('student/attendance/', views.view_attendance, name='view_attendance'),

    # Schedules / Events
    path('teacher/schedules/', views.teacher_schedules, name='teacher_schedules'),
    path('teacher/schedules/upload/', views.upload_schedule, name='upload_schedule'),
    path('teacher/schedules/<int:schedule_id>/edit/', views.edit_schedule, name='edit_schedule'),
    path('teacher/schedules/<int:schedule_id>/delete/', views.delete_schedule, name='delete_schedule'),
    path('schedules/', views.student_schedules, name='student_schedules'),
    path('schedules/broadcast-notifications/', views.schedule_broadcast_notifications, name='schedule_broadcast_notifications'),

    # Quick actions for teachers
    path('teacher/assignment/create/', views.create_assignment, name='create_assignment'),
    path('teacher/assignment/new/', views.render_create_assignment, name='render_create_assignment'),
    path('teacher/assignment/import-url/', views.import_from_url, name='import_from_url'),
    path('teacher/assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('teacher/assignment/<int:assignment_id>/download/', views.download_assignment_report, name='download_assignment_report'),
    path('teacher/course/<int:course_id>/report/', views.generate_course_report, name='generate_course_report'),
    path('teacher/course/<int:course_id>/report/pdf/', views.generate_course_report_pdf, name='generate_course_report_pdf'),
    path('teacher/course/<int:course_id>/students-json/', views.course_students_json, name='course_students_json'),
    path('teacher/course/<int:course_id>/student/<int:student_id>/report/', views.teacher_student_report, name='teacher_student_report'),
    path('teacher/course/<int:course_id>/assignment-averages/', views.generate_assignment_averages, name='generate_assignment_averages'),
    path('teacher/send-message/', views.send_message, name='send_message'),


    # Profile management
    path('profile/', views_profile.view_profile, name='view_profile'),
    path('profile/edit/', views_profile.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views_profile.view_profile, name='view_profile_user'),
    path('profile/update-photo/', views_profile.update_profile_photo, name='update_profile_photo'),

    # Reports
    path('student/download-report/', views.download_student_report, name='download_report'),
    path('teacher/download-report/', views.download_teacher_report, name='download_teacher_report'),

    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-as-read/', views.mark_as_read, name='mark_as_read'),
    path('notifications/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),

    # Course catalog and certificates
    path('courses/', views.course_catalog, name='course_catalog'),
    path('certificates/', views.my_certificates, name='my_certificates'),

    # Simple admin page (separate from Django admin)
    path('admin-page/', views.admin_page, name='admin_page'),
    # Admin2 (powerful sub-admin) panel routes
    path('admin2/dashboard/', views.admin2_dashboard, name='admin2_dashboard'),
    path('admin2/financial/', views.admin2_financial, name='admin2_financial'),
    path('admin2/staff/', views.admin2_staff, name='admin2_staff'),
    path('admin2/staff/add/<int:profile_id>/', views.admin2_add_staff, name='admin2_add_staff'),
    path('admin2/staff/remove/<int:staff_id>/', views.admin2_remove_staff, name='admin2_remove_staff'),
    path('admin2/payouts/', views.admin2_payouts, name='admin2_payouts'),
    path('admin2/notifications/', views.admin2_notifications, name='admin2_notifications'),
    path('admin2/add-salary/', views.admin2_add_salary, name='admin2_add_salary'),
    path('admin2/record-fee/', views.admin2_record_fee, name='admin2_record_fee'),
    path('admin2/export-financial/', views.admin2_export_financial_excel, name='admin2_export_financial_excel'),
    path('admin2/payouts/<int:payout_id>/process/', views.admin2_process_payout, name='admin2_process_payout'),
    path('admin2/updates/', views.admin2_updates, name='admin2_updates'),
    # One-click attendance and related endpoints
    path('admin2/attendance/one-click/', views.one_click_attendance, name='one_click_attendance'),
    path('admin2/attendance/summary/', views.admin2_attendance_summary, name='admin2_attendance_summary'),
    path('admin2/attendance/export/', views.admin2_export_attendance, name='admin2_export_attendance'),
    path('admin2/attendance/ai-insights/', views.admin2_attendance_ai_insights, name='admin2_attendance_ai_insights'),
    path('admin2/attendance/list/', views.admin2_attendance_list, name='admin2_attendance_list'),
    # Admin2 student payments and exports
    path('admin2/student/<int:student_id>/payments/', views.admin2_student_payments, name='admin2_student_payments'),
    path('admin2/student/<int:student_id>/payments/export/csv/', views.export_student_payments_csv, name='export_student_payments_csv'),
    path('admin2/student/<int:student_id>/payments/export/pdf/', views.export_student_payments_pdf, name='export_student_payments_pdf'),
    # Admin exports (use superadmin/ prefix to avoid colliding with Django admin/)
    path('superadmin/export-users/', views.export_users_pdf, name='export_users_pdf'),
    path('superadmin/download-report/<int:user_id>/', views.download_student_report_admin, name='admin_download_student_report'),
    
    # New export endpoints for student lists
    path('superadmin/export/students/pdf/', views.export_selected_students_pdf, name='export_selected_students_pdf'),
    path('superadmin/export/students/excel/', views.export_selected_students_excel, name='export_selected_students_excel'),
]