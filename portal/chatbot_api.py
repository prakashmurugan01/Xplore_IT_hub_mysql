"""
Advanced Chatbot API endpoints for real-time student-teacher-admin communication
Features: Real-time messaging, notification delivery, message history, and intelligent routing
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from django.db.models import Q
from .models import Notification, Profile, Enrollment
from .chatbot_service import StudentChatbotService
import json


@login_required
@require_POST
def chatbot_message(request):
    """
    Handle student chatbot messages with AI-powered responses
    Supports all intent types: courses, assignments, attendance, contact, help, etc.
    """
    try:
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return JsonResponse({'success': False, 'error': 'Access denied - Student role required'}, status=403)
        
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            }, status=400)
        
        # Initialize chatbot service with student profile
        student_profile = request.user.profile
        chatbot = StudentChatbotService(student_profile)
        
        # Process message and get intelligent response
        response = chatbot.process_message(message)
        
        return JsonResponse({
            'success': True,
            'response': response,
            'user_message': message,
            'timestamp': timezone.now().isoformat()
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': 'Server error occurred',
            'response': {
                'type': 'error',
                'message': '❌ An error occurred. Please try again.',
                'timestamp': timezone.now().isoformat()
            }
        }, status=500)


@login_required
@require_POST
def send_message_to_teacher(request):
    """
    Send a message from student to teacher with real-time notification
    Creates Notification record that teachers see in real-time
    """
    try:
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
        
        data = json.loads(request.body)
        teacher_name = data.get('teacher_name', '').strip()
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return JsonResponse({'success': False, 'error': 'Message cannot be empty'}, status=400)
        
        if not teacher_name:
            return JsonResponse({'success': False, 'error': 'Teacher name required'}, status=400)
        
        # Find teacher by name from student's enrolled courses
        student = request.user.profile
        enrollments = Enrollment.objects.filter(student=student).select_related('course__teacher')
        
        teacher_profile = None
        for enrollment in enrollments:
            teacher = enrollment.course.teacher
            teacher_full_name = teacher.user.get_full_name() or teacher.user.username
            if teacher_full_name.lower() == teacher_name.lower():
                teacher_profile = teacher
                break
        
        if not teacher_profile:
            return JsonResponse({
                'success': False,
                'error': f'Teacher "{teacher_name}" not found in your courses'
            }, status=404)
        
        # Create notification for teacher with real-time indicator
        notification = Notification.objects.create(
            user=teacher_profile.user,
            title=f"💬 New Message from {student.user.get_full_name()}",
            message=message_text,
            type='student_message',
            is_read=False,
            created_at=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'message': f"✅ Message sent to {teacher_profile.user.get_full_name()} successfully!",
            'teacher_name': teacher_profile.user.get_full_name(),
            'notification_id': notification.id,
            'timestamp': timezone.now().isoformat(),
            'suggestions': ['Contact another teacher', 'Back to Menu']
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def send_message_to_admin(request):
    """
    Send a message from student to all admins with categorization
    Real-time notifications delivered to all admin2/superadmin users
    """
    try:
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
        
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        category = data.get('category', 'general').lower()
        
        if not message_text:
            return JsonResponse({'success': False, 'error': 'Message cannot be empty'}, status=400)
        
        # Get all admin users
        admin_profiles = Profile.objects.filter(
            role__in=['admin2', 'superadmin']
        ).select_related('user')
        
        if not admin_profiles.exists():
            return JsonResponse({
                'success': False,
                'message': '❌ No administrators available. Please try again later.'
            })
        
        # Category emojis for visual indication
        category_info = {
            'technical': {'emoji': '🛠️', 'label': 'Technical Issue'},
            'enrollment': {'emoji': '📋', 'label': 'Enrollment Query'},
            'fee': {'emoji': '💰', 'label': 'Fee Issue'},
            'complaint': {'emoji': '⚠️', 'label': 'Complaint'},
            'general': {'emoji': '💬', 'label': 'General Query'}
        }
        
        category_data = category_info.get(category, category_info['general'])
        
        # Create notifications for all admins
        notifications_created = []
        for admin in admin_profiles:
            notification = Notification.objects.create(
                user=admin.user,
                title=f"{category_data['emoji']} {category_data['label']} from {request.user.get_full_name()}",
                message=message_text,
                type='student_query',
                is_read=False,
                created_at=timezone.now()
            )
            notifications_created.append(notification.id)
        
        return JsonResponse({
            'success': True,
            'message': f"{category_data['emoji']} Your message has been sent to {len(notifications_created)} administrator(s)!",
            'category': category,
            'admins_notified': len(notifications_created),
            'timestamp': timezone.now().isoformat(),
            'suggestions': ['Contact teacher', 'Back to Menu']
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_teacher_list(request):
    """
    Get list of all teachers from student's enrolled courses
    Includes email and course information for real-time contact
    """
    try:
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
        
        student = request.user.profile
        
        # Get all teachers from student's enrolled courses
        enrollments = Enrollment.objects.filter(student=student).select_related('course__teacher__user')
        
        teachers_dict = {}
        
        for enrollment in enrollments:
            teacher = enrollment.course.teacher
            if teacher.id not in teachers_dict:
                teachers_dict[teacher.id] = {
                    'id': teacher.id,
                    'name': teacher.user.get_full_name() or teacher.user.username,
                    'email': teacher.user.email,
                    'courses': []
                }
            teachers_dict[teacher.id]['courses'].append({
                'id': enrollment.course.id,
                'name': enrollment.course.name,
                'code': enrollment.course.code
            })
        
        teacher_list = list(teachers_dict.values())
        
        return JsonResponse({
            'success': True,
            'teachers': teacher_list,
            'count': len(teacher_list),
            'timestamp': timezone.now().isoformat()
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_admin_list(request):
    """
    Get list of all administrators available for contact
    Includes admin names, emails, and roles
    """
    try:
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
        
        # Get all admins
        admin_profiles = Profile.objects.filter(
            role__in=['admin2', 'superadmin']
        ).select_related('user')
        
        admins = []
        for admin in admin_profiles:
            admins.append({
                'id': admin.id,
                'name': admin.user.get_full_name() or admin.user.username,
                'email': admin.user.email,
                'role': admin.role,
                'role_display': 'Superadmin' if admin.role == 'superadmin' else 'Administrator'
            })
        
        return JsonResponse({
            'success': True,
            'admins': admins,
            'count': len(admins),
            'timestamp': timezone.now().isoformat()
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_message_history(request):
    """
    Get chat message history for a specific contact (teacher or admin)
    Returns past conversations for context
    """
    try:
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
        
        contact_type = request.GET.get('type', 'teacher')  # 'teacher' or 'admin'
        contact_id = request.GET.get('contact_id')
        
        if not contact_id:
            return JsonResponse({'success': False, 'error': 'contact_id required'}, status=400)
        
        # Get notifications (messages) with this contact
        if contact_type == 'teacher':
            try:
                contact = Profile.objects.get(id=contact_id, role='teacher')
                messages = Notification.objects.filter(
                    Q(user=request.user, title__contains=contact.user.get_full_name()) |
                    Q(user=contact.user, title__contains=request.user.get_full_name())
                ).order_by('-created_at')[:20]
            except Profile.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Teacher not found'}, status=404)
        
        elif contact_type == 'admin':
            try:
                contact = Profile.objects.get(id=contact_id, role__in=['admin2', 'superadmin'])
                messages = Notification.objects.filter(
                    Q(user=request.user, title__contains=contact.user.get_full_name()) |
                    Q(user=contact.user, title__contains=request.user.get_full_name())
                ).order_by('-created_at')[:20]
            except Profile.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Admin not found'}, status=404)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid contact type'}, status=400)
        
        message_list = [
            {
                'id': msg.id,
                'message': msg.message,
                'timestamp': msg.created_at.isoformat(),
                'is_from_student': msg.user.id == request.user.id
            }
            for msg in messages
        ]
        
        return JsonResponse({
            'success': True,
            'messages': message_list,
            'count': len(message_list)
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
