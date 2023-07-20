from django import template

register = template.Library()


def concat_string(value_1, value_2):
    return "%s%s" % (value_1, value_2)


register.filter('concat_string', concat_string)
