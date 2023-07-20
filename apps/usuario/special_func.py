from django.utils.http import is_safe_url, urlunquote


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_next_url(request):
    next = request.META.get('HTTP_REFERER')
    if next:
        next = urlunquote(next)  # HTTP_REFERER may be encoded.
    if not is_safe_url(url=next, allowed_hosts=request.get_host()):
        next = '/'
    return next
