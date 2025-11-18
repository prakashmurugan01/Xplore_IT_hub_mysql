from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

class Profile(models.Model):
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin2', 'Admin 2'),
        ('finance', 'Finance'),
        ('staff', 'Staff'),
        ('teacher', 'Teacher'),
        ('student', 'Student')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    # New fields for student management
    student_class = models.CharField(max_length=50, blank=True, null=True)
    roll_number = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

# Auto-create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Only save profile if it exists (defensive guard for edge cases)
    if hasattr(instance, 'profile') and instance.profile is not None:
        instance.profile.save()


class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    teacher = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'teacher'}
    )
    credits = models.IntegerField(default=3)
    semester = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Enrollment(models.Model):
    student = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'student'}
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.course.code}"


class Attendance(models.Model):
    student = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'student'}
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=False)  # True = Present, False = Absent
    
    class Meta:
        unique_together = ['student', 'course', 'date']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.course.code} - {self.date}"


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    # Short rich-text description (HTML allowed) and optional body for longer formatted content
    description = models.TextField(blank=True)
    body = models.TextField(blank=True)
    # Draft flag to support saving drafts from the UI
    is_draft = models.BooleanField(default=False)
    # Allow assignments with no due date (drafts / open-ended)
    due_date = models.DateField(null=True, blank=True)
    max_marks = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'student'}
    )
    submission_date = models.DateTimeField(auto_now_add=True)
    # Optional file uploaded by student when submitting
    file = models.FileField(upload_to='submissions/', null=True, blank=True)
    # Student's submitted text
    text = models.TextField(blank=True)
    marks_obtained = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title}"


class AssignmentAttachment(models.Model):
    """Files or images attached to an assignment. Teachers may upload multiple files."""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='assignments/')
    uploaded_by = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.assignment.id} - {self.file.name}"


class Question(models.Model):
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True / False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
        ('file_upload', 'File Upload'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    order = models.IntegerField(default=0)
    qtype = models.CharField(max_length=20, choices=QUESTION_TYPES, default='mcq')
    text = models.TextField()
    points = models.FloatField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order} ({self.qtype}) - {self.text[:40]}"


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    order = models.IntegerField(default=0)
    text = models.CharField(max_length=1000)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Option {self.order} for Q{self.question.order}: {self.text[:40]}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"# Database


class StudyMaterial(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.code} - {self.title}"


class Feedback(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.student.user.username} on {self.course.code if self.course else 'General'}"


class Certificate(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issued_date = models.DateTimeField(auto_now_add=True)
    certificate_id = models.CharField(max_length=50, unique=True)
    file = models.FileField(upload_to='certificates/')
    grade = models.CharField(max_length=2, blank=True, null=True)
    completion_date = models.DateField()
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.course.code} Certificate"
    
    def save(self, *args, **kwargs):
        if not self.certificate_id:
            # Generate a unique certificate ID
            import uuid
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


# Administrative / Financial models for admin2 role
class StaffMember(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, blank=True)
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.user.username} ({self.position})"


class SalaryRecord(models.Model):
    staff = models.ForeignKey(StaffMember, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Salary {self.amount} to {self.staff.profile.user.username} on {self.paid_on}"


class FeePayment(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, default='paid')

    def __str__(self):
        return f"Fee {self.amount} by {self.student.user.username} on {self.paid_on}"


class StudentPayout(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    requested_on = models.DateTimeField(auto_now_add=True)
    processed_on = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Payout {self.amount} to {self.student.user.username} ({self.status})"


class FinancialTransaction(models.Model):
    TRAN_TYPE = [('credit', 'Credit'), ('debit', 'Debit')]
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    trans_type = models.CharField(max_length=10, choices=TRAN_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.trans_type} {self.amount} ({self.title})"


# Staff attendance records (basic MVP). In production consider using a dedicated face-recognition
# service or adding more metadata and an audit trail. Making staff FK nullable so unknown/failed
# recognitions can still be recorded.
class StaffAttendance(models.Model):
    staff = models.ForeignKey('StaffMember', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50, default='webcam')
    recognized_username = models.CharField(max_length=150, blank=True, null=True)
    image = models.ImageField(upload_to='attendance/', null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        who = self.recognized_username or (self.staff.profile.user.username if self.staff and getattr(self.staff, 'profile', None) else 'unknown')
        return f"Attendance {who} @ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class StaffDailyAttendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
    ]

    staff = models.ForeignKey('StaffMember', on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    timestamp = models.DateTimeField(auto_now=True)
    method = models.CharField(max_length=50, default='system')
    note = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-date', '-timestamp']
        unique_together = (('staff', 'date'),)

    def __str__(self):
        who = getattr(self.staff, 'profile', None) and getattr(self.staff.profile, 'user', None)
        who_name = who.get_full_name() if who else (getattr(who, 'username', 'unknown') if who else 'unknown')
        return f"{who_name} - {self.date.isoformat()} - {self.status}"


# Simple schedule/events model for teachers to post class schedules or events
class ScheduleManager(models.Manager):
    def upcoming_for_student(self, profile):
        # Returns public schedules or those tied to student's enrolled courses from today onwards
        enrollments = Enrollment.objects.filter(student=profile).values_list('course_id', flat=True)
        today = timezone.localdate()
        return self.filter(
            models.Q(is_active=True),
            models.Q(date__gte=today),
            models.Q(is_public=True) | models.Q(course_id__in=list(enrollments))
        ).order_by('date', 'start_time')

    def upcoming_for_teacher(self, profile):
        # Returns schedules created by the teacher
        today = timezone.localdate()
        return self.filter(created_by=profile, is_active=True, date__gte=today).order_by('date', 'start_time')


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Schedule(models.Model):
    """Advanced schedule/event model.

    Features:
    - Optional recurrence rule (RFC5545 RRULE string stored)
    - Reminder minutes for notifications
    - Soft-delete via `is_active`
    - Tags for categorization
    - Slug for stable URLs
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, blank=True, db_index=True)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    timezone = models.CharField(max_length=64, default='UTC')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    created_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    notify_students = models.BooleanField(default=False)
    reminder_minutes = models.IntegerField(default=30)
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(max_length=500, blank=True, help_text='RRULE string, e.g. FREQ=WEEKLY;BYDAY=MO')
    color = models.CharField(max_length=20, blank=True, help_text='Optional color for calendar display')
    tags = models.ManyToManyField(Tag, blank=True)
    attachment = models.FileField(upload_to='schedules/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ScheduleManager()

    class Meta:
        ordering = ['-date', '-start_time']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.title}-{self.date.isoformat()}"
            self.slug = slugify(base)[:250]
        # Ensure created_by_user mirrors created_by (if available)
        if not self.created_by_user and self.created_by and getattr(self.created_by, 'user', None):
            self.created_by_user = self.created_by.user
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} @ {self.date} ({self.course.code if self.course else 'General'})"


# When a schedule is created and notify_students=True, create Notification entries for affected students
@receiver(post_save, sender=Schedule)
def schedule_post_save(sender, instance, created, **kwargs):
    """
    Send notifications when a schedule is created and notify_students=True.
    Targets: enrolled students (if course-linked) + teacher, OR all students+teachers (if public)
    """
    if not created:
        return  # Only on creation
    
    if not instance.notify_students or not instance.is_active:
        return  # Only if enabled
    
    try:
        # Collect target users: students and teachers depending on course/public
        targets = set()
        
        if instance.course:
            # Students enrolled in the course
            enrollments = Enrollment.objects.filter(course=instance.course).select_related('student__user')
            for e in enrollments:
                if getattr(e.student, 'user', None):
                    targets.add(e.student.user)
            
            # Include the course teacher if available
            teacher_profile = getattr(instance.course, 'teacher', None)
            if teacher_profile and getattr(teacher_profile, 'user', None):
                targets.add(teacher_profile.user)
        
        elif instance.is_public:
            # Broadcast to all students and teachers
            profiles = Profile.objects.filter(role__in=['student', 'teacher']).select_related('user')
            for p in profiles:
                if getattr(p, 'user', None):
                    targets.add(p.user)
        
        # Build notification message
        title = f"📅 Schedule: {instance.title}"
        msg = f"{instance.title} on {instance.date}"
        if instance.start_time:
            msg += f" at {instance.start_time}"
        if instance.course:
            msg += f" ({instance.course.code})"
        else:
            msg += " (Public Event)"
        
        # Create notifications for all targets
        notifications_created = 0
        for u in targets:
            try:
                Notification.objects.create(
                    user=u, 
                    title=title, 
                    message=msg,
                    is_read=False
                )
                notifications_created += 1
            except Exception as e:
                print(f"Failed to create notification for user {u}: {e}")
                continue
        
        print(f"✓ Schedule notifications sent: {notifications_created} users notified")
        
    except Exception as e:
        # Do not allow notification failures to break schedule save
        print(f"Error in schedule_post_save: {e}")
        import traceback
        traceback.print_exc()