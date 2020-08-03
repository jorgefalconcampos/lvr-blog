#This template tag highlights the post title/subtitle according to a given query in a search form

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='highlight')
def highlight(text, search):
    highlighted = text.replace(search, '<span class="highlight">{}</span>'.format(search))
    return mark_safe(highlighted)