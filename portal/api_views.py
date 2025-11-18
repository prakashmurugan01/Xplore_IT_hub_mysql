from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Attendance, Assignment, Notification, Course, Enrollment, StudyMaterial, Feedback
from django.utils import timezone
from django.db.models import Q, Count, Avg
import datetime
import json

@login_required
def get_student_tasks(request):
    """API endpoint to fetch student tasks/assignments."""
    try:
        if not hasattr(request.user, 'profile') or getattr(request.user.profile, 'role', None) != 'student':
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        student = request.user.profile
        now = timezone.now()
        now_date = now.date()
        
        # Get pending assignments
        enrollments = Enrollment.objects.filter(student=student).values_list('course', flat=True)
        assignments = Assignment.objects.filter(
            course_id__in=enrollments
        ).order_by('-due_date')[:10]
        
        tasks = []
        for assignment in assignments:
            due_date = assignment.due_date
            if isinstance(due_date, datetime.datetime):
                due_date = due_date.date()
            
            due_str = due_date.strftime('%Y-%m-%d') if due_date else 'N/A'
            is_pending = due_date and due_date >= now_date if due_date else False
            days_left = (due_date - now_date).days if due_date else None
            
            tasks.append({
                'id': assignment.id,
                'title': assignment.title,
                'due': due_str,
                'status': 'pending' if is_pending else 'overdue',
                'priority': 'high' if days_left is not None and days_left <= 3 else 'medium',
                'course': assignment.course.name if assignment.course else 'Unknown'
            })
        
        return JsonResponse({'tasks': tasks, 'count': len(tasks)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_student_materials(request):
    """API endpoint to fetch latest study materials."""
    try:
        if not hasattr(request.user, 'profile') or getattr(request.user.profile, 'role', None) != 'student':
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        student = request.user.profile
        enrollments = Enrollment.objects.filter(student=student).values_list('course', flat=True)
        materials = StudyMaterial.objects.filter(
            course_id__in=enrollments
        ).order_by('-uploaded_at')[:10]
        
        materials_list = []
        for material in materials:
            materials_list.append({
                'id': material.id,
                'title': material.title,
                'course': material.course.name if material.course else 'Unknown',
                'uploaded_at': material.uploaded_at.strftime('%Y-%m-%d %H:%M') if material.uploaded_at else 'N/A',
                'file_type': material.file.name.split('.')[-1].upper() if material.file else 'LINK',
                'download_url': material.file.url if material.file else material.url
            })
        
        return JsonResponse({'materials': materials_list})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_student_timetable(request):
    """API endpoint to fetch student timetable."""
    try:
        if not hasattr(request.user, 'profile') or getattr(request.user.profile, 'role', None) != 'student':
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        student = request.user.profile
        enrollments = Enrollment.objects.filter(student=student).select_related('course')
        
        # Generate a sample timetable (customize based on your schedule model)
        timetable = []
        courses = [e.course for e in enrollments]
        
        # Example schedule
        schedule_template = [
            {'day': 'Mon', 'time': '9:00-10:30', 'subject': 'Data Structures', 'staff': 'Dr. Asha'},
            {'day': 'Tue', 'time': '11:00-12:30', 'subject': 'Operating Systems', 'staff': 'Mr. Ravi'},
            {'day': 'Wed', 'time': '2:00-3:30', 'subject': 'Database Systems', 'staff': 'Ms. Nisha'},
        ]
        
        for schedule in schedule_template:
            timetable.append(schedule)
        
        return JsonResponse({'timetable': timetable})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_student_events(request):
    """API endpoint to fetch upcoming events."""
    if getattr(request.user.profile, 'role', None) != 'student':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        # Sample events - customize based on your event model
        events = [
            {
                'title': 'Tech Seminar: AI Trends',
                'venue': 'Hall A',
                'date': '2025-11-21'
            },
            {
                'title': 'Project Expo',
                'venue': 'Lobby',
                'date': '2025-12-05'
            }
        ]
        
        return JsonResponse({'events': events})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_student_notifications(request):
    """API endpoint to fetch student notifications."""
    try:
        if not hasattr(request.user, 'profile') or getattr(request.user.profile, 'role', None) != 'student':
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Get notifications for the user
        try:
            notifications = Notification.objects.filter(
                user=request.user
            ).order_by('-created_at')[:10]
        except Exception as e:
            print(f"Error fetching notifications: {e}")
            notifications = []
        
        notif_list = []
        for notif in notifications:
            try:
                notif_list.append({
                    'id': notif.id,
                    'title': getattr(notif, 'title', 'Notification'),
                    'message': getattr(notif, 'message', str(notif)),
                    'type': getattr(notif, 'type', 'info'),
                    'created_at': notif.created_at.strftime('%Y-%m-%d %H:%M') if notif.created_at else 'N/A',
                    'is_read': getattr(notif, 'is_read', False)
                })
            except Exception as e:
                print(f"Error processing notification {notif.id}: {e}")
                continue
        
        unread_count = len([n for n in notif_list if not n['is_read']])
        
        return JsonResponse({
            'notifications': notif_list, 
            'unread_count': unread_count,
            'total_count': len(notif_list)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'notifications': [],
            'unread_count': 0,
            'total_count': 0,
            'error': str(e)
        }, status=200)


@login_required
def get_student_courses(request):
    """API endpoint to fetch student enrolled courses."""
    try:
        if not hasattr(request.user, 'profile') or getattr(request.user.profile, 'role', None) != 'student':
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        student = request.user.profile
        
        # Get all courses the student is enrolled in
        enrollments = Enrollment.objects.filter(student=student).select_related('course')
        
        courses_list = []
        for enrollment in enrollments:
            course = enrollment.course
            courses_list.append({
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'credits': course.credits,
                'semester': course.semester,
                'teacher': course.teacher.user.get_full_name() or course.teacher.user.username,
                'exam_date': 'TBD'  # Can be extended if Exam model exists
            })
        
        return JsonResponse({'courses': courses_list})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_student_attendance(request):
    """API endpoint to fetch real-time attendance data.

    This endpoint returns both a course-wise breakdown used by the
    dashboard front-end (``courses`` + ``overall``) and the weekly
    history (``weekly`` / ``historyPercents``) so older clients remain
    compatible.
    """
    try:
        if not hasattr(request.user, 'profile') or getattr(request.user.profile, 'role', None) != 'student':
            return JsonResponse({'error': 'Access denied'}, status=403)

        student = request.user.profile

        # Aggregate overall totals
        attendance_records = Attendance.objects.filter(student=student).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status=True))
        )

        total = attendance_records.get('total', 0) or 0
        present = attendance_records.get('present', 0) or 0
        percent = round((present / total) * 100, 1) if total > 0 else 0

        # Per-course breakdown (match frontend expectation)
        enrollments = Enrollment.objects.filter(student=student).select_related('course')
        attendance_data = []
        for enrollment in enrollments:
            course = enrollment.course
            records = Attendance.objects.filter(student=student, course=course)
            present_count = records.filter(status=True).count()
            total_count = records.count()
            pct = round((present_count / total_count) * 100, 1) if total_count > 0 else 0
            attendance_data.append({
                'course_id': course.id,
                'course_name': course.name,
                'course_code': course.code,
                'present': present_count,
                'total': total_count,
                'percentage': pct
            })

        # Weekly breakdown for the last 5 weeks (keeps compatibility)
        now = timezone.now().date()
        weekly_data = []
        for i in range(5, 0, -1):
            week_start = now - datetime.timedelta(weeks=i)
            week_end = week_start + datetime.timedelta(days=7)
            week_records = Attendance.objects.filter(student=student, date__gte=week_start, date__lt=week_end)
            week_total = week_records.count()
            week_present = week_records.filter(status=True).count()
            week_pct = round((week_present / week_total) * 100, 1) if week_total > 0 else 0
            weekly_data.append({'week': f'W{i}', 'present': week_present, 'total': week_total or 0, 'percent': week_pct})

        return JsonResponse({
            'courses': attendance_data,
            'overall': {'present': present, 'total': total, 'percentage': percent},
            'weekly': weekly_data,
            'historyPercents': [w['percent'] for w in weekly_data]
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)



@login_required
def get_latest_uploads(request):
    """API endpoint for fetching latest material uploads."""
    if getattr(request.user.profile, 'role', None) != 'student':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    student = request.user.profile
    try:
        enrollments = Enrollment.objects.filter(student=student).values_list('course', flat=True)
        materials = StudyMaterial.objects.filter(
            course_id__in=enrollments
        ).order_by('-uploaded_at')[:5]
        
        uploads = []
        for material in materials:
            uploads.append({
                'id': material.id,
                'title': material.title,
                'course': material.course.name if material.course else 'Unknown'
            })
        
        return JsonResponse(uploads, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_live_updates(request):
    """API endpoint to fetch live updates for the student dashboard.
    Returns updates for attendance, assignments, exams, and course content.
    """
    if getattr(request.user.profile, 'role', None) != 'student':
        return JsonResponse({'error': 'Access denied'}, status=403)

    student = request.user.profile
    now = timezone.now()
    updates = []

    # Get enrolled courses
    enrolled_courses = Course.objects.filter(
        enrollment__student=student
    )

    # Recent attendance records (last 24 hours)
    recent_attendance = Attendance.objects.filter(
        student=student,
        date__gte=now.date()
    ).select_related('course')

    for attendance in recent_attendance:
        updates.append({
            'type': 'attendance',
            'title': f'Attendance recorded for {attendance.course.name}',
            'timestamp': attendance.date.strftime('%I:%M %p'),
            'is_new': True
        })

    # New assignments (added in last 24 hours)
    new_assignments = Assignment.objects.filter(
        course__in=enrolled_courses,
        created_at__gte=now - datetime.timedelta(days=1)
    ).select_related('course')

    for assignment in new_assignments:
        updates.append({
            'type': 'assignment',
            'title': f'New assignment: {assignment.title}',
            'timestamp': assignment.created_at.strftime('%I:%M %p'),
            'is_new': True
        })

    # Recent exam schedules or results (if any)
    # This is a placeholder - add actual exam model queries when implemented
    # updates.append({
    #     'type': 'exam',
    #     'title': 'Mid-term results published',
    #     'timestamp': '2 hours ago',
    #     'is_new': False
    # })

    # New course content or materials
    recent_materials = StudyMaterial.objects.filter(
        course__in=enrolled_courses,
        uploaded_at__gte=now - datetime.timedelta(days=1)
    ).select_related('course')

    for material in recent_materials:
        updates.append({
            'type': 'course',
            'title': f'New material added to {material.course.name}: {material.title}',
            'timestamp': material.uploaded_at.strftime('%I:%M %p'),
            'is_new': True
        })

    # Sort updates by timestamp (newest first) and limit to 10
    updates.sort(key=lambda x: x['timestamp'], reverse=True)
    updates = updates[:10]

    return JsonResponse({
        'updates': updates
    })


@login_required
def get_analytics(request):
    """Return study analytics and AI recommendations for the current user.

    Payload example:
    {
      peak_hours: '9 AM - 11 AM',
      avg_session: '1.5 hours',
      weekly_total: 28.5,
      learning_style: { labels: [...], values: [...] },
      ai_tips: [{title, description}, ...],
      achievements: [{title, progress, status}, ...]
    }
    """
    if getattr(request.user.profile, 'role', None) != 'student':
        return JsonResponse({'error': 'Access denied'}, status=403)

    student = request.user.profile
    now = timezone.now()

    # Example heuristics — replace with real analytics when available
    peak_hours = '9 AM - 11 AM'
    avg_session = 1.5
    weekly_total = 28.5

    # Learning style mock (visual, auditory, kinesthetic)
    learning_style = {
        'labels': ['Visual', 'Auditory', 'Hands-on', 'Reading'],
        'values': [45, 20, 25, 10]
    }

    # AI tips — in real app, call predictor for personalized tips
    ai_tips = [
        {'title': 'Focus on Django ORM', 'description': 'Your recent quiz results suggest reviewing database relationships.'},
        {'title': 'Practice Python Debugging', 'description': 'Spend more time on error handling exercises.'}
    ]

    achievements = [
        {'title': '7-Day Streak', 'progress': 100, 'status': 'completed'},
        {'title': 'Quick Learner', 'progress': 80, 'status': 'in-progress'},
        {'title': 'Team Player', 'progress': 60, 'status': 'in-progress'},
        {'title': 'Code Master', 'progress': 45, 'status': 'in-progress'},
    ]

    data = {
        'peak_hours': peak_hours,
        'avg_session': avg_session,
        'weekly_total': weekly_total,
        'learning_style': learning_style,
        'ai_tips': ai_tips,
        'achievements': achievements,
        'last_updated': now.isoformat(),
    }

    return JsonResponse(data)


@login_required
@login_required
def get_student_schedules(request):
    """API endpoint to fetch upcoming schedules for students.
    
    Returns Schedule objects relevant to student's enrolled courses + public schedules.
    Sorted by date ascending (nearest first).
    """
    try:
        if not hasattr(request.user, 'profile') or getattr(request.user.profile, 'role', None) != 'student':
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        from .models import Schedule
        
        student = request.user.profile
        schedules = Schedule.objects.upcoming_for_student(student)
        
        schedules_list = []
        for sched in schedules:
            schedules_list.append({
                'id': sched.id,
                'title': sched.title,
                'description': sched.description,
                'date': sched.date.isoformat(),
                'start_time': sched.start_time.isoformat() if sched.start_time else None,
                'end_time': sched.end_time.isoformat() if sched.end_time else None,
                'location': sched.location,
                'course': sched.course.code if sched.course else 'General',
                'is_public': sched.is_public,
                'color': sched.color,
                'attachment_url': sched.attachment.url if sched.attachment else None,
            })
        
        return JsonResponse({'schedules': schedules_list, 'count': len(schedules_list)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_schedule_notifications(request):
    """API endpoint for teachers/admins to fetch schedule-related notifications.
    
    Returns notifications where the message mentions 'Schedule' or 'Event'.
    Useful for tracking broadcast confirmations.
    """
    try:
        user_role = getattr(request.user.profile, 'role', None)
        if user_role not in ['teacher', 'admin2', 'superadmin']:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Fetch schedule/event notifications for this user (received broadcasts)
        notifications = Notification.objects.filter(
            user=request.user,
            title__icontains='Schedule'
        ).order_by('-created_at')[:20]
        
        notif_list = []
        for notif in notifications:
            notif_list.append({
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'created_at': notif.created_at.isoformat(),
                'is_read': notif.is_read,
            })
        
        return JsonResponse({
            'notifications': notif_list,
            'count': len(notif_list),
            'unread_count': Notification.objects.filter(user=request.user, title__icontains='Schedule', is_read=False).count()
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)