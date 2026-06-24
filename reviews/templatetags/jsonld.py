from django import template
from django.utils.safestring import mark_safe

from reviews.seo import json_ld

register = template.Library()


@register.filter
def to_json_ld(value):
    return mark_safe(json_ld(value))
