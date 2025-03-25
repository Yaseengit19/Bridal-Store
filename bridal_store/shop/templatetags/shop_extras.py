from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def add_days(date_str, days):
    """Add specified number of days to a date string"""
    try:
        date_format = "%b %d, %Y"
        date_obj = datetime.strptime(date_str, date_format)
        new_date = date_obj + timedelta(days=int(days))
        return new_date.strftime(date_format)
    except:
        return date_str

@register.filter
def less_than(value1, value2):
    """Compare two values"""
    try:
        return int(value1) < int(value2)
    except:
        return False