from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect


def is_role(user, role_name):
    """Return True if the user has the given profile role name."""
    try:
        return getattr(user, 'profile', None) and getattr(user.profile, 'role', None) == role_name
    except Exception:
        return False


def is_any_role(user, roles):
    """Return True if the user has any role in the iterable `roles`."""
    try:
        r = getattr(user, 'profile', None) and getattr(user.profile, 'role', None)
        return r in roles
    except Exception:
        return False


def role_required(roles):
    """Decorator to require one or more roles for a view.

    Usage:
      @role_required('superadmin')
      @role_required(['superadmin','admin2'])
    """
    if isinstance(roles, str):
        allowed = {roles}
    else:
        allowed = set(roles)

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not is_any_role(user, allowed):
                # If it's an AJAX/JSON request, return 403 JSON, else redirect
                if request.is_ajax() or request.headers.get('Accept','').lower().startswith('application/json'):
                    return JsonResponse({'error': 'Access denied'}, status=403)
                # fallback: add a message and redirect to role_redirect if available
                try:
                    from django.contrib import messages
                    messages.error(request, 'Access denied!')
                except Exception:
                    pass
                return redirect('role_redirect')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
