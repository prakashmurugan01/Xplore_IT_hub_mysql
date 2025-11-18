from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Course, Certificate

@login_required
def course_catalog(request):
    """View for browsing all available courses"""
    courses = Course.objects.all().order_by('-created_at')
    context = {
        'courses': courses,
        'page_title': 'Course Catalog'
    }
    return render(request, 'courses/catalog.html', context)

def my_certificates(request):
    """View for displaying student's earned certificates"""
    certificates = Certificate.objects.filter(student=request.user.profile)
    context = {
        'certificates': certificates,
        'page_title': 'My Certificates'
    }
    return render(request, 'certificates/list.html', context)