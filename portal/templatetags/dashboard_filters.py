from django import template

register = template.Library()

@register.filter(name='activity_icon')
def activity_icon(activity_type):
    """Return the appropriate Font Awesome icon class based on activity type."""
    icons = {
        'performance': 'fa-chart-line',
        'attendance': 'fa-user-check',
        'assignment': 'fa-tasks',
        'exam': 'fa-file-alt',
        'course': 'fa-book',
        'material': 'fa-file-pdf',
        'notification': 'fa-bell',
        'feedback': 'fa-comment',
        'achievement': 'fa-trophy',
        'project': 'fa-project-diagram',
        'discussion': 'fa-comments',
        'submission': 'fa-upload',
        'grade': 'fa-star',
        'meeting': 'fa-video',
        'deadline': 'fa-clock',
    }
    return icons.get(activity_type, 'fa-circle-info')  # default icon if type not found