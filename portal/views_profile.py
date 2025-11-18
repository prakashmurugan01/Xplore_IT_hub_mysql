from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db.models import Avg, Count
from .models import Profile, Enrollment, Attendance, Submission, Course
from django.utils.text import slugify
import os

@login_required
def view_profile(request, username=None):
    """Enhanced profile view that shows role-specific information."""
    # If no username provided, show current user's profile
    if username is None:
        profile = request.user.profile
    else:
        # Try to find user by exact username first
        try:
            profile = Profile.objects.select_related('user').get(user__username=username)
        except Profile.DoesNotExist:
            # Try matching by slugified full name
            profiles = Profile.objects.select_related('user').all()
            profile = None
            for p in profiles:
                full_name = f"{p.user.first_name} {p.user.last_name}".strip()
                if slugify(full_name) == username or slugify(p.user.username) == username:
                    profile = p
                    break
            if not profile:
                messages.error(request, 'Profile not found')
                return redirect('role_redirect')

    context = {
        'profile': profile,
        'full_name': f"{profile.user.first_name} {profile.user.last_name}".strip() or profile.user.username,
        'email': profile.user.email,
        'phone': getattr(profile, 'phone', ''),
        'department': getattr(profile, 'department', ''),
        'profile_pic': profile.profile_pic.url if getattr(profile, 'profile_pic', None) else None,
    }

    if profile.role == 'student':
        # Get student-specific stats
        enrollments = Enrollment.objects.filter(student=profile)
        
        # Attendance stats
        total_attendance = Attendance.objects.filter(student=profile).count()
        present = Attendance.objects.filter(student=profile, status=True).count()
        attendance_rate = (present / total_attendance * 100) if total_attendance > 0 else 0
        
        # Academic performance
        submissions = Submission.objects.filter(student=profile)
        avg_marks = submissions.aggregate(Avg('marks_obtained'))['marks_obtained__avg'] or 0
        
        # Course performance breakdown
        course_performance = []
        for enrollment in enrollments:
            course_submissions = submissions.filter(assignment__course=enrollment.course)
            course_avg = course_submissions.aggregate(Avg('marks_obtained'))['marks_obtained__avg'] or 0
            course_attendance = Attendance.objects.filter(student=profile, course=enrollment.course)
            course_attendance_rate = (course_attendance.filter(status=True).count() / course_attendance.count() * 100) if course_attendance.exists() else 0
            
            course_performance.append({
                'course': enrollment.course,
                'avg_marks': round(course_avg, 2),
                'attendance': round(course_attendance_rate, 2)
            })

        context.update({
            'student_class': getattr(profile, 'student_class', ''),
            'roll_number': getattr(profile, 'roll_number', ''),
            'attendance_rate': round(attendance_rate, 2),
            'avg_marks': round(avg_marks, 2),
            'total_courses': enrollments.count(),
            'course_performance': course_performance
        })

    elif profile.role == 'teacher':
        # Get teacher-specific stats
        courses = Course.objects.filter(teacher=profile)
        total_students = Enrollment.objects.filter(course__teacher=profile).values('student').distinct().count()
        
        # Teaching stats
        course_stats = []
        for course in courses:
            enrollments = Enrollment.objects.filter(course=course)
            attendance = Attendance.objects.filter(course=course)
            attendance_rate = (attendance.filter(status=True).count() / attendance.count() * 100) if attendance.exists() else 0
            
            submissions = Submission.objects.filter(assignment__course=course)
            avg_marks = submissions.aggregate(Avg('marks_obtained'))['marks_obtained__avg'] or 0
            
            course_stats.append({
                'course': course,
                'students': enrollments.count(),
                'attendance_rate': round(attendance_rate, 2),
                'avg_marks': round(avg_marks, 2)
            })

        context.update({
            'total_courses': courses.count(),
            'total_students': total_students,
            'course_stats': course_stats
        })

    return render(request, 'profile/view_profile.html', context)

@login_required
def edit_profile(request):
    """Allow users to edit their own profile information."""
    if request.method == 'POST':
        profile = request.user.profile
        
        # Update user info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        # Update profile info
        profile.phone = request.POST.get('phone', '')
        profile.department = request.POST.get('department', '')
        
        if profile.role == 'student':
            profile.student_class = request.POST.get('student_class', '')
            profile.roll_number = request.POST.get('roll_number', '')
        
        # Handle profile photo upload
        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('view_profile')
        
    return render(request, 'profile/edit_profile.html', {'profile': request.user.profile})

@login_required
def update_profile_photo(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        # Get the uploaded file
        photo = request.FILES['photo']
        
        # Delete old profile photo if it exists
        if request.user.profile.profile_pic:
            try:
                old_photo_path = request.user.profile.profile_pic.path
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)
            except:
                pass
        
        # Generate a unique filename
        file_ext = os.path.splitext(photo.name)[1]
        filename = f'profiles/user_{request.user.id}_profile{file_ext}'
        
        # Save the new photo
        file_path = default_storage.save(filename, photo)
        request.user.profile.profile_pic = file_path
        request.user.profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profile photo updated successfully',
            'photo_url': request.user.profile.profile_pic.url
        })
    
    return JsonResponse({
        'success': False,
        'message': 'No photo provided'
    })