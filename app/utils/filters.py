from datetime import datetime
from flask import Blueprint

filters_bp = Blueprint('filters', __name__)

@filters_bp.app_template_filter('timeago')
def timeago_filter(date):
    """Convert a datetime to a 'time ago' string."""
    now = datetime.utcnow()
    diff = now - date
    
    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days
    months = days // 30
    years = days // 365
    
    if seconds < 60:
        return "just now"
    elif minutes < 60:
        return f"{int(minutes)} minute{'s' if minutes != 1 else ''} ago"
    elif hours < 24:
        return f"{int(hours)} hour{'s' if hours != 1 else ''} ago"
    elif days < 30:
        return f"{int(days)} day{'s' if days != 1 else ''} ago"
    elif months < 12:
        return f"{int(months)} month{'s' if months != 1 else ''} ago"
    else:
        return f"{int(years)} year{'s' if years != 1 else ''} ago"