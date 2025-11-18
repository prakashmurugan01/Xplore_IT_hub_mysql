from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portal.models import Profile, Course, Enrollment, Assignment, Submission, Attendance
from django.utils import timezone
import random
from datetime import timedelta, date
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Seed demo data for Xplorehub'

    def handle(self, *args, **options):
        # Create superadmin
        if not User.objects.filter(username='superadmin').exists():
            su = User.objects.create_superuser('superadmin', 'superadmin@example.com', 'password')
            su_profile = su.profile
            su_profile.role = 'superadmin'
            su_profile.save()
            self.stdout.write(self.style.SUCCESS('Created superadmin'))

        # Create requested admin user for quick login (username: xplore_admin02, password: admin)
        if not User.objects.filter(username='xplore_admin02').exists():
            try:
                admin_user = User.objects.create_user('xplore_admin02', 'xplore_admin02@example.com', 'admin')
                admin_user.is_staff = True
                admin_user.save()
                admin_user.profile.role = 'superadmin'
                admin_user.profile.save()
                self.stdout.write(self.style.SUCCESS('Created xplore_admin02 (password: admin)'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to create xplore_admin02: {e}'))

        # Create teacher
        if not User.objects.filter(username='teacher1').exists():
            t = User.objects.create_user('teacher1', 'teacher1@example.com', 'password')
            t.profile.role = 'teacher'
            t.profile.save()
            self.stdout.write(self.style.SUCCESS('Created teacher1'))

        # Create student
        if not User.objects.filter(username='student1').exists():
            s = User.objects.create_user('student1', 'student1@example.com', 'password')
            s.profile.role = 'student'
            s.profile.save()
            self.stdout.write(self.style.SUCCESS('Created student1'))

        # Create course
        teacher_profile = Profile.objects.filter(role='teacher').first()
        student_profile = Profile.objects.filter(role='student').first()
        if teacher_profile and student_profile:
            # Use code as unique identifier and set other fields via defaults to avoid unique constraint errors
            try:
                course, created = Course.objects.get_or_create(code='TEST101', defaults={'name': 'Intro to Testing', 'teacher': teacher_profile})
                if created:
                    self.stdout.write(self.style.SUCCESS('Created course TEST101'))
            except IntegrityError:
                # If a race or previous partial insert created the course, fetch it by code
                course = Course.objects.filter(code='TEST101').first()
                if course:
                    self.stdout.write(self.style.WARNING('Course TEST101 already exists (fetched existing)'))
                else:
                    raise

            # Enroll student
            enrollment, created = Enrollment.objects.get_or_create(student=student_profile, course=course)
            if created:
                self.stdout.write(self.style.SUCCESS('Enrolled student1 in TEST101'))

            # Create assignment and submission
            assignment, created = Assignment.objects.get_or_create(course=course, title='Homework 1', defaults={'due_date': date.today() + timedelta(days=7), 'max_marks': 100})
            if created:
                self.stdout.write(self.style.SUCCESS('Created assignment Homework 1'))

            submission, created = Submission.objects.get_or_create(assignment=assignment, student=student_profile, defaults={'marks_obtained': 75})
            if created:
                self.stdout.write(self.style.SUCCESS('Created submission for student1'))

            # Create attendance records for last 5 days
            for i in range(5):
                d = date.today() - timedelta(days=i)
                # Avoid unique constraint problems by checking existence first
                att = Attendance.objects.filter(student=student_profile, course=course, date=d).first()
                if att:
                    att.status = random.choice([True, True, False])
                    att.save()
                else:
                    try:
                        Attendance.objects.create(student=student_profile, course=course, date=d, status=random.choice([True, True, False]))
                    except IntegrityError:
                        # If another process created it in the meantime, skip
                        continue
            self.stdout.write(self.style.SUCCESS('Created attendance records'))

        self.stdout.write(self.style.SUCCESS('Demo data seeding complete'))
