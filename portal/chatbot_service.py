"""
Advanced AI Chatbot Service for Student Dashboard
Handles intelligent responses, message routing, and real-time communications with real teacher/admin messaging
"""

import re
from django.utils import timezone
from django.db.models import Q
from .models import Course, Assignment, Enrollment, Attendance, Notification, Profile
from datetime import datetime, timedelta


class StudentChatbotService:
    """
    Intelligent chatbot service for students with NLP capabilities and real-time messaging
    """
    
    INTENTS = {
        'greeting': {
            'keywords': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening'],
            'responses': [
                "👋 Hello! I'm your AI Study Assistant. How can I help you today?",
                "Hi there! 📚 What do you need help with?",
                "Welcome! I'm here to assist with courses, assignments, and more. What's on your mind?"
            ]
        },
        'courses': {
            'keywords': ['course', 'subject', 'class', 'enrolled', 'credits', 'semester'],
            'method': 'get_courses_info'
        },
        'assignments': {
            'keywords': ['assignment', 'task', 'work', 'project', 'deadline', 'due', 'submit'],
            'method': 'get_assignments_info'
        },
        'attendance': {
            'keywords': ['attendance', 'present', 'absent', 'classes', 'attendance percentage', 'bunk'],
            'method': 'get_attendance_info'
        },
        'schedule': {
            'keywords': ['schedule', 'timetable', 'when', 'time', 'class timing', 'exam'],
            'method': 'get_schedule_info'
        },
        'materials': {
            'keywords': ['material', 'notes', 'resources', 'document', 'pdf', 'download'],
            'method': 'get_materials_info'
        },
        'help': {
            'keywords': ['help', 'support', 'how', 'what can', 'capabilities', 'features', 'assistance'],
            'responses': [
                "I can help you with:\n📚 Courses & Enrollment\n✅ Assignments & Deadlines\n📊 Attendance Records\n📅 Class Schedule\n📖 Study Materials\n\nJust ask about any of these!",
                "You can ask me about:\n• Your enrolled courses\n• Pending assignments\n• Your attendance\n• Class timetable\n• Available materials\n• Connect with teachers/admins"
            ]
        },
        'contact_teacher': {
            'keywords': ['contact teacher', 'message teacher', 'ask teacher', 'teacher', 'professor', 'instructor'],
            'responses': [
                "📧 I can help you connect with your teachers! Would you like to send them a message?\nWhich course's teacher would you like to contact?"
            ]
        },
        'contact_admin': {
            'keywords': ['admin', 'administrator', 'principal', 'contact admin', 'report issue'],
            'responses': [
                "👨‍💼 Need to reach administration? I can help connect you with our admin team.\nWhat's your message about?"
            ]
        },
        'gratitude': {
            'keywords': ['thanks', 'thank you', 'appreciate', 'great', 'excellent', 'good job'],
            'responses': [
                "😊 You're welcome! Happy to help!",
                "Glad I could assist! Is there anything else?",
                "Thanks! Let me know if you need help with anything else. 📚"
            ]
        },
        'farewell': {
            'keywords': ['bye', 'goodbye', 'see you', 'later', 'exit', 'close'],
            'responses': [
                "👋 Goodbye! Good luck with your studies!",
                "See you later! Keep up the great work! 🌟",
                "Bye! Don't hesitate to reach out if you need help. 📚"
            ]
        }
    }
    
    def __init__(self, student_profile):
        self.student = student_profile
        self.user = student_profile.user
    
    def process_message(self, message):
        """
        Process user message and return intelligent response
        """
        if not message or not message.strip():
            return {
                'type': 'error',
                'message': '❌ Please enter a message.',
                'timestamp': timezone.now().isoformat()
            }
        
        message_lower = message.lower().strip()
        
        # Detect intent
        intent = self._detect_intent(message_lower)
        
        # Route to appropriate handler
        if intent == 'greeting':
            return self._generate_greeting_response()
        elif intent == 'help':
            return self._generate_help_response()
        elif intent == 'courses':
            return self._get_courses_info()
        elif intent == 'assignments':
            return self._get_assignments_info()
        elif intent == 'attendance':
            return self._get_attendance_info()
        elif intent == 'schedule':
            return self._get_schedule_info()
        elif intent == 'materials':
            return self._get_materials_info()
        elif intent == 'contact_teacher':
            return self._get_contact_teacher_info()
        elif intent == 'contact_admin':
            return self._get_contact_admin_info()
        elif intent == 'gratitude':
            return self._generate_gratitude_response()
        elif intent == 'farewell':
            return self._generate_farewell_response()
        else:
            return self._generate_default_response(message)
    
    def _detect_intent(self, message):
        """Detect user's intent from message"""
        for intent, config in self.INTENTS.items():
            keywords = config.get('keywords', [])
            for keyword in keywords:
                if keyword in message:
                    return intent
        return 'unknown'
    
    def _generate_greeting_response(self):
        import random
        response = random.choice(self.INTENTS['greeting']['responses'])
        return {
            'type': 'greeting',
            'message': response,
            'timestamp': timezone.now().isoformat(),
            'suggestions': ['My Courses', 'Assignments', 'Attendance', 'Help']
        }
    
    def _generate_help_response(self):
        import random
        response = random.choice(self.INTENTS['help']['responses'])
        return {
            'type': 'help',
            'message': response,
            'timestamp': timezone.now().isoformat()
        }
    
    def _generate_gratitude_response(self):
        import random
        response = random.choice(self.INTENTS['gratitude']['responses'])
        return {
            'type': 'gratitude',
            'message': response,
            'timestamp': timezone.now().isoformat()
        }
    
    def _generate_farewell_response(self):
        import random
        response = random.choice(self.INTENTS['farewell']['responses'])
        return {
            'type': 'farewell',
            'message': response,
            'timestamp': timezone.now().isoformat()
        }
    
    def _generate_default_response(self, message):
        """Generate default response for unknown queries"""
        return {
            'type': 'default',
            'message': f"🤔 I understood you asked: '{message}'\n\nTry asking me about:\n• 📚 Your courses\n• ✅ Your assignments\n• 📊 Your attendance\n• 📅 Class schedule\n• 📖 Study materials\n\nOr type 'help' for more options!",
            'timestamp': timezone.now().isoformat(),
            'suggestions': ['My Courses', 'Assignments', 'Attendance', 'Help']
        }
    
    def _get_courses_info(self):
        """Get student's enrolled courses"""
        try:
            enrollments = Enrollment.objects.filter(student=self.student).select_related('course')
            
            if not enrollments.exists():
                return {
                    'type': 'courses',
                    'message': '📚 You are not enrolled in any courses yet.',
                    'timestamp': timezone.now().isoformat()
                }
            
            courses_text = "📚 **Your Enrolled Courses:**\n\n"
            for enrollment in enrollments:
                course = enrollment.course
                courses_text += f"• **{course.code}** - {course.name}\n  👨‍🏫 {course.teacher.user.get_full_name()}\n  ⭐ {course.credits} Credits\n\n"
            
            return {
                'type': 'courses',
                'message': courses_text,
                'timestamp': timezone.now().isoformat(),
                'count': enrollments.count(),
                'suggestions': ['Assignments', 'Attendance', 'Materials']
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f'❌ Error fetching courses: {str(e)}',
                'timestamp': timezone.now().isoformat()
            }
    
    def _get_assignments_info(self):
        """Get student's pending assignments"""
        try:
            enrollments = Enrollment.objects.filter(student=self.student).values_list('course', flat=True)
            assignments = Assignment.objects.filter(
                course_id__in=enrollments,
                due_date__gte=timezone.now().date()
            ).order_by('due_date')[:10]
            
            if not assignments.exists():
                return {
                    'type': 'assignments',
                    'message': '✅ Great! You have no pending assignments.',
                    'timestamp': timezone.now().isoformat()
                }
            
            assign_text = "✅ **Your Pending Assignments:**\n\n"
            for assignment in assignments:
                days_left = (assignment.due_date - timezone.now().date()).days
                emoji = "🔴" if days_left <= 2 else "🟡" if days_left <= 7 else "🟢"
                assign_text += f"{emoji} **{assignment.title}**\n   📚 {assignment.course.name}\n   ⏰ Due: {assignment.due_date.strftime('%b %d, %Y')} ({days_left} days left)\n\n"
            
            return {
                'type': 'assignments',
                'message': assign_text,
                'timestamp': timezone.now().isoformat(),
                'count': assignments.count(),
                'urgent': any((a.due_date - timezone.now().date()).days <= 2 for a in assignments),
                'suggestions': ['Courses', 'Materials', 'Help']
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f'❌ Error fetching assignments: {str(e)}',
                'timestamp': timezone.now().isoformat()
            }
    
    def _get_attendance_info(self):
        """Get student's attendance statistics"""
        try:
            attendance_records = Attendance.objects.filter(student=self.student).aggregate(
                total=__import__('django.db.models', fromlist=['Count']).Count('id'),
                present=__import__('django.db.models', fromlist=['Count']).Count('id', filter=Q(status=True))
            )
            
            total = attendance_records.get('total', 0) or 0
            present = attendance_records.get('present', 0) or 0
            
            if total == 0:
                return {
                    'type': 'attendance',
                    'message': '📊 No attendance records yet.',
                    'timestamp': timezone.now().isoformat()
                }
            
            percentage = (present / total) * 100
            emoji = "🟢" if percentage >= 75 else "🟡" if percentage >= 60 else "🔴"
            
            attend_text = f"{emoji} **Your Attendance:**\n\n"
            attend_text += f"📊 Overall: **{percentage:.1f}%**\n"
            attend_text += f"✓ Present: **{present}** classes\n"
            attend_text += f"✗ Absent: **{total - present}** classes\n"
            attend_text += f"📈 Total: **{total}** classes\n\n"
            
            if percentage < 75:
                attend_text += "⚠️ Your attendance is below 75%. Try to attend more classes!"
            else:
                attend_text += "✨ Great attendance! Keep it up!"
            
            return {
                'type': 'attendance',
                'message': attend_text,
                'timestamp': timezone.now().isoformat(),
                'percentage': percentage,
                'present': present,
                'total': total
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f'❌ Error fetching attendance: {str(e)}',
                'timestamp': timezone.now().isoformat()
            }
    
    def _get_schedule_info(self):
        """Get student's class schedule"""
        return {
            'type': 'schedule',
            'message': "📅 **Your Class Schedule:**\n\nMon: 9:00-10:30 - Data Structures (Dr. Asha)\nTue: 11:00-12:30 - Operating Systems (Mr. Ravi)\nWed: 2:00-3:30 - Database Systems (Ms. Nisha)\nThu: 10:00-11:30 - Web Development (Mr. Arjun)\nFri: 1:00-2:30 - Project Lab (Prof. Sharma)",
            'timestamp': timezone.now().isoformat(),
            'suggestions': ['Assignments', 'Attendance', 'Courses']
        }
    
    def _get_materials_info(self):
        """Get available study materials"""
        try:
            enrollments = Enrollment.objects.filter(student=self.student).values_list('course', flat=True)
            from .models import StudyMaterial
            materials = StudyMaterial.objects.filter(
                course_id__in=enrollments
            ).order_by('-uploaded_at')[:5]
            
            if not materials.exists():
                return {
                    'type': 'materials',
                    'message': '📖 No study materials available yet.',
                    'timestamp': timezone.now().isoformat()
                }
            
            mat_text = "📖 **Latest Study Materials:**\n\n"
            for material in materials:
                mat_text += f"📄 **{material.title}**\n   📚 {material.course.name}\n   📅 {material.uploaded_at.strftime('%b %d, %Y')}\n\n"
            
            return {
                'type': 'materials',
                'message': mat_text,
                'timestamp': timezone.now().isoformat(),
                'count': materials.count(),
                'suggestions': ['Courses', 'Assignments', 'Help']
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f'❌ Error fetching materials: {str(e)}',
                'timestamp': timezone.now().isoformat()
            }
    
    def _get_contact_teacher_info(self):
        """Get teacher contact information with real teacher names from database"""
        try:
            # Get all teachers from enrolled courses
            enrollments = Enrollment.objects.filter(student=self.student).select_related('course__teacher')
            teachers = {}
            
            for enrollment in enrollments:
                teacher = enrollment.course.teacher
                teacher_name = teacher.user.get_full_name() or teacher.user.username
                if teacher.id not in teachers:
                    teachers[teacher.id] = {
                        'name': teacher_name,
                        'user_id': teacher.user.id,
                        'email': teacher.user.email,
                        'courses': [enrollment.course.name]
                    }
                else:
                    if enrollment.course.name not in teachers[teacher.id]['courses']:
                        teachers[teacher.id]['courses'].append(enrollment.course.name)
            
            if not teachers:
                return {
                    'type': 'contact',
                    'message': "📧 **Contact Your Teachers:**\n\n❌ No teachers found in your enrolled courses.",
                    'timestamp': timezone.now().isoformat(),
                    'action': 'contact_teacher',
                    'suggestions': ['Back to Menu']
                }
            
            # Format teacher list with courses
            message = "📧 **Contact Your Teachers:**\n\n✨ Select a teacher to send a direct message:\n\n"
            teacher_suggestions = []
            
            for teacher_id, teacher_info in teachers.items():
                courses_str = ', '.join(teacher_info['courses'][:2])  # Show first 2 courses
                message += f"👨‍🏫 **{teacher_info['name']}** 📧 ({teacher_info['email']})\n   📚 {courses_str}\n\n"
                teacher_suggestions.append(teacher_info['name'])
            
            message += "💬 Click on a teacher name or type their name to send a message."
            
            return {
                'type': 'contact',
                'message': message,
                'timestamp': timezone.now().isoformat(),
                'action': 'contact_teacher',
                'teachers': teachers,
                'suggestions': teacher_suggestions + ['Back to Menu']
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f'❌ Error fetching teachers: {str(e)}',
                'timestamp': timezone.now().isoformat()
            }
    
    def _get_contact_admin_info(self):
        """Get admin contact information with real admin names"""
        try:
            # Get all admin users
            admins = Profile.objects.filter(
                role__in=['admin2', 'superadmin']
            ).select_related('user')
            
            if not admins.exists():
                return {
                    'type': 'contact',
                    'message': "👨‍💼 **Contact Administration:**\n\n❌ No admins available.",
                    'timestamp': timezone.now().isoformat(),
                    'action': 'contact_admin',
                    'suggestions': ['Back to Menu']
                }
            
            message = "👨‍💼 **Contact Administration:**\n\n✨ Our admin team is here to help:\n\n"
            admin_suggestions = []
            admins_list = []
            
            for admin in admins:
                admin_name = admin.user.get_full_name() or admin.user.username
                role_display = "🔑 Superadmin" if admin.role == 'superadmin' else "👤 Admin"
                message += f"{role_display} **{admin_name}** 📧 ({admin.user.email})\n"
                admin_suggestions.append(admin_name)
                admins_list.append({
                    'id': admin.id,
                    'user_id': admin.user.id,
                    'name': admin_name,
                    'email': admin.user.email,
                    'role': admin.role
                })
            
            message += "\n💬 Select an admin or type your message directly.\n"
            message += "📋 **Common Issues:** Technical problems, Enrollment, Fee, Complaint, General Query\n"
            
            return {
                'type': 'contact',
                'message': message,
                'timestamp': timezone.now().isoformat(),
                'action': 'contact_admin',
                'admins': admins_list,
                'suggestions': admin_suggestions + ['General Query', 'Technical Issue', 'Complaint', 'Back to Menu']
            }
        except Exception as e:
            return {
                'type': 'error',
                'message': f'❌ Error fetching admins: {str(e)}',
                'timestamp': timezone.now().isoformat()
            }
    
    def send_message_to_teacher(self, teacher_id, message_text):
        """Send message to teacher and create notification with real-time delivery"""
        try:
            teacher = Profile.objects.get(id=teacher_id, role='teacher')
            
            # Create notification for teacher
            notification = Notification.objects.create(
                recipient=teacher.user,
                sender=self.user,
                title=f"New message from {self.student.user.get_full_name()}",
                message=message_text,
                notification_type='message',
                is_read=False
            )
            
            return {
                'success': True,
                'message': f"✅ Message sent to {teacher.user.get_full_name()} successfully!",
                'timestamp': timezone.now().isoformat(),
                'notification_id': notification.id,
                'suggestions': ['Contact another teacher', 'Back to Menu']
            }
        except Profile.DoesNotExist:
            return {
                'success': False,
                'message': '❌ Teacher not found.',
                'timestamp': timezone.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ Error sending message: {str(e)}',
                'timestamp': timezone.now().isoformat()
            }
    
    def send_message_to_admin(self, message_text, issue_category='general'):
        """Send message to all admins with categorization"""
        try:
            admins = Profile.objects.filter(role__in=['admin2', 'superadmin']).values_list('user', flat=True)
            
            if not admins.exists():
                return {
                    'success': False,
                    'message': '❌ No admins available.',
                    'timestamp': timezone.now().isoformat()
                }
            
            notifications_created = 0
            
            for admin_user_id in admins:
                notification = Notification.objects.create(
                    recipient_id=admin_user_id,
                    sender=self.user,
                    title=f"Student Message: [{issue_category.upper()}] from {self.student.user.get_full_name()}",
                    message=message_text,
                    notification_type='message',
                    is_read=False
                )
                notifications_created += 1
            
            category_emoji = {
                'technical': '🛠️',
                'enrollment': '📋',
                'fee': '💰',
                'complaint': '⚠️',
                'general': '💬'
            }.get(issue_category, '💬')
            
            return {
                'success': True,
                'message': f"{category_emoji} Your message has been sent to {notifications_created} admin(s)!",
                'timestamp': timezone.now().isoformat(),
                'admins_notified': notifications_created,
                'suggestions': ['Contact teacher', 'Back to Menu']
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ Error sending message: {str(e)}',
                'timestamp': timezone.now().isoformat()
            }
