import re

from django import template

register = template.Library()


@register.filter(name='censor')
def censor(value):
    if isinstance(value, str):
        return re.sub('мат1|мат2|мат3', '#@$%', value)
    else:
        raise ValueError('Недопустимый тип в фильтре censor')