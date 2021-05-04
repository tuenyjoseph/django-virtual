import datetime
from django.utils import timezone
from django import template

register = template.Library()

@register.filter
def minutes_ago(time, minutes):
    return time + datetime.timedelta(minutes=minutes) > timezone.now()

@register.filter
def hours_ago(time, hours):
    return time + datetime.timedelta(hours=hours) > timezone.now()

@register.filter
def days_ago(time, days):
    return time + datetime.timedelta(days=days) > timezone.now()