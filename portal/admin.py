from django.contrib import admin
from django.http import HttpResponse
import csv
from django.utils import timezone

from .models import (
    Profile, Course, Enrollment, Attendance, Assignment, Submission,
    Notification, Schedule, Tag, StudyMaterial, Certificate
)


# Admin site branding
admin.site.site_header = 'XploreHub Admin'
admin.site.site_title = 'XploreHub Administration'
admin.site.index_title = 'Site Administration'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'phone']
    list_filter = ['role', 'department']
    search_fields = ['user__username', 'user__email']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'teacher', 'credits', 'semester']
    list_filter = ['semester', 'credits']
    search_fields = ['name', 'code']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_date']
    list_filter = ['enrolled_date', 'course']
    search_fields = ['student__user__username', 'course__name']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'date', 'status']
    list_filter = ['status', 'date', 'course']
    search_fields = ['student__user__username', 'course__name']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'due_date', 'max_marks']
    list_filter = ['due_date', 'course']
    search_fields = ['title', 'course__name']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'submission_date', 'marks_obtained']
    list_filter = ['submission_date', 'assignment']
    search_fields = ['student__user__username', 'assignment__title']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'title']


def export_schedules_csv(modeladmin, request, queryset):
    """Admin action: export selected schedules as CSV."""
    meta = modeladmin.model._meta
    field_names = ['id', 'title', 'date', 'start_time', 'end_time', 'course', 'created_by', 'is_public', 'is_active']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=schedules_export_%s.csv' % timezone.now().strftime('%Y%m%d_%H%M%S')
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([
            getattr(obj, 'id', ''),
            getattr(obj, 'title', ''),
            getattr(obj, 'date', ''),
            getattr(obj, 'start_time', ''),
            getattr(obj, 'end_time', ''),
            (obj.course.code if getattr(obj, 'course', None) else ''),
            (obj.created_by.user.username if getattr(obj, 'created_by', None) and getattr(obj.created_by, 'user', None) else ''),
            obj.is_public,
            obj.is_active,
        ])
    return response


def notify_selected_students(modeladmin, request, queryset):
    """Admin action: create Notification records for students affected by selected schedules."""
    created = 0
    for sched in queryset:
        targets = []
        if sched.course:
            enrollments = Enrollment.objects.filter(course=sched.course).select_related('student__user')
            for e in enrollments:
                if getattr(e.student, 'user', None):
                    targets.append(e.student.user)
            # include the course teacher if available
            teacher_profile = getattr(sched.course, 'teacher', None)
            if teacher_profile and getattr(teacher_profile, 'user', None):
                targets.append(teacher_profile.user)
        elif sched.is_public:
            # Broadcast to all students and teachers
            targets = [p.user for p in Profile.objects.filter(role__in=['student', 'teacher']) if getattr(p, 'user', None)]

        title = f"Schedule: {sched.title}"
        message = f"{sched.title} on {sched.date}"
        if sched.start_time:
            message += f" at {sched.start_time}"

        for u in targets:
            try:
                Notification.objects.create(user=u, title=title, message=message)
                created += 1
            except Exception:
                continue
    modeladmin.message_user(request, f"Notifications created for {created} recipients.")


def mark_active(modeladmin, request, queryset):
    queryset.update(is_active=True)
    modeladmin.message_user(request, "Selected schedules marked active.")


def mark_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)
    modeladmin.message_user(request, "Selected schedules marked inactive.")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'start_time', 'end_time', 'course', 'created_by', 'is_public', 'is_active', 'notify_students']
    list_filter = ['date', 'is_public', 'is_active', 'is_recurring', 'created_by__role']
    search_fields = ['title', 'description', 'course__name', 'course__code', 'created_by__user__username']
    actions = [export_schedules_csv, notify_selected_students, mark_active, mark_inactive]
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at', 'slug']
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'course', 'location', 'date', 'start_time', 'end_time', 'timezone')
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('is_public', 'is_active', 'is_recurring', 'recurrence_rule', 'notify_students', 'reminder_minutes', 'tags', 'color', 'attachment')
        }),
        ('Meta', {
            'fields': ('created_by', 'created_by_user', 'created_at', 'updated_at')
        }),
    )


@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'uploaded_by', 'uploaded_at']
    list_filter = ['course', 'uploaded_at']
    search_fields = ['title', 'description', 'course__name']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'certificate_id', 'issued_date']
    search_fields = ['student__user__username', 'certificate_id']