from django import template

register = template.Library()


def currency(dollars):
    import locale
    # Set to users preferred locale:
    locale.setlocale(locale.LC_ALL, 'es_EC.UTF-8')
    #locale.setlocale(locale.LC_ALL, '')

    return locale.currency(dollars)


register.filter('currency', currency)
