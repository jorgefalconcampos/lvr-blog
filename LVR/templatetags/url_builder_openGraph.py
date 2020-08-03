#This template tag creates an absolute URL for static files for its use in open graph protocol

from django import template
from django.templatetags import static

register = template.Library()

class FullStaticNode(static.StaticNode):
    def url(self, context):
        request = context['request']
        return request.build_absolute_uri(super().url(context))

@register.tag('fullstatic')
def do_static(parser, token):
    return FullStaticNode.handle_token(parser, token)