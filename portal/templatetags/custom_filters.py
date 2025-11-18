from django import template

register = template.Library()

@register.filter(name='attendance_badge')
def attendance_badge(value):
    """Return appropriate badge class based on attendance percentage"""
    try:
        attendance = float(value)
        if attendance >= 90:
            return 'success'
        elif attendance >= 75:
            return 'warning'
        else:
            return 'danger'
    except (ValueError, TypeError):
        return 'warning'

@register.filter(name='abs')
def abs_filter(value):
    """Return absolute value"""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0

@register.filter(name='trend_arrow')
def trend_arrow(value):
    """Return appropriate arrow direction based on trend value"""
    try:
        trend = float(value)
        if trend > 0:
            return 'up'
        elif trend < 0:
            return 'down'
        else:
            return 'right'
    except (ValueError, TypeError):
        return 'right'

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0