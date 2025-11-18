from .models import Notification


def unread_notifications(request):
    """Return unread notification count for the logged-in user, or 0."""
    if request.user.is_authenticated:
        try:
            count = Notification.objects.filter(user=request.user, is_read=False).count()
        except Exception:
            count = 0
    else:
        count = 0
    return {'unread_count': count}
