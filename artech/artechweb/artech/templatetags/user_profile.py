from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.simple_tag(takes_context=True)
def get_user_position(context):
    user = context['user']
    if user.is_authenticated:
        try:
            return user.profile.position
        except:
            return ''
    return ''
