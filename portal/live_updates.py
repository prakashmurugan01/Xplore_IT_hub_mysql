def get_student_live_updates(student_profile):
    """Helper function to generate live updates for a student."""
    from django.utils import timezone
    import datetime

    # Current timezone and today's date (aware-aware comparisons will use aware datetimes)
    tz = timezone.get_current_timezone()
    today = timezone.localtime(timezone.now(), timezone=tz).date()
    
    # Initialize empty updates list
    updates = []
    
    # Add performance updates (from recent submissions)
    # Use aware range for DB lookup: compute cutoff as aware datetime at start of day
    cutoff_date = today - datetime.timedelta(days=7)
    cutoff_dt = timezone.make_aware(datetime.datetime.combine(cutoff_date, datetime.time.min), tz)
    submissions = student_profile.submission_set.filter(
        submission_date__gte=cutoff_dt
    ).select_related('assignment', 'assignment__course')
    
    for sub in submissions:
        if sub.marks_obtained is not None:
            score = round(sub.marks_obtained / sub.assignment.max_marks * 100, 2)
            # Normalize submission_date to timezone-aware in current tz
            sub_ts = getattr(sub, 'submission_date', None)
            if sub_ts is None:
                continue
            try:
                sub_ts = timezone.localtime(sub_ts, timezone=tz)
            except Exception:
                # If sub_ts is naive, make it aware then convert
                sub_ts = timezone.make_aware(sub_ts, tz)

            updates.append({
                'type': 'performance',
                'title': f'Marks received for {sub.assignment.title}',
                'timestamp': sub_ts,
                'is_new': sub_ts.date() == today,
                'score': score,
                'score_class': 'success' if score >= 70 else 'warning' if score >= 50 else 'danger',
                'details': f'Course: {sub.assignment.course.name}'
            })
    
    # Add attendance updates
    attendances = student_profile.attendance_set.filter(
        date__gte=today - datetime.timedelta(days=7)
    ).select_related('course')
    
    for att in attendances:
        # Combine date to datetime at midnight and make it aware
        att_dt = datetime.datetime.combine(att.date, datetime.time.min)
        try:
            att_ts = timezone.make_aware(att_dt, tz)
        except Exception:
            # If already aware, ensure in local tz
            att_ts = timezone.localtime(att_dt, timezone=tz)

        updates.append({
            'type': 'attendance',
            'title': f'Attendance recorded for {att.course.name}',
            'timestamp': att_ts,
            'is_new': att.date == today,
            'status': 'Present' if att.status else 'Absent',
            'status_class': 'success' if att.status else 'danger',
            'details': f'Date: {att.date.strftime("%d %b %Y")}'
        })
    
    # Add course updates (from assignments)
    assignments = student_profile.course_set.filter(
        assignment__due_date__gte=today
    ).values_list('assignment__title', 'assignment__due_date', 'name').order_by('assignment__due_date')
    
    for title, due_date, course_name in assignments:
        due_dt = datetime.datetime.combine(due_date, datetime.time.min)
        try:
            due_ts = timezone.make_aware(due_dt, tz)
        except Exception:
            due_ts = timezone.localtime(due_dt, timezone=tz)

        updates.append({
            'type': 'assignment',
            'title': f'New assignment: {title}',
            'timestamp': due_ts,
            'is_new': False,  # Only new when first created
            'details': f'Due date: {due_date.strftime("%d %b %Y")} | Course: {course_name}'
        })
    
    # Add material updates
    materials = student_profile.course_set.filter(
        studymaterial__uploaded_at__gte=today - datetime.timedelta(days=7)
    ).values_list('studymaterial__title', 'studymaterial__uploaded_at', 'name')
    
    for title, uploaded_at, course_name in materials:
        # Ensure uploaded_at is timezone-aware
        uploaded_ts = uploaded_at
        try:
            if getattr(uploaded_ts, 'tzinfo', None) is None:
                uploaded_ts = timezone.make_aware(uploaded_ts, tz)
            else:
                uploaded_ts = timezone.localtime(uploaded_ts, timezone=tz)
        except Exception:
            # Fallback: use current time
            uploaded_ts = timezone.localtime(timezone.now(), timezone=tz)

        updates.append({
            'type': 'material',
            'title': f'New study material: {title}',
            'timestamp': uploaded_ts,
            'is_new': uploaded_ts.date() == today,
            'details': f'Course: {course_name}'
        })
    
    # Sort all updates by timestamp in descending order
    updates.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return updates[:10]  # Return only the 10 most recent updates