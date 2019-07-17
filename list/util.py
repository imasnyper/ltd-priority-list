from django.conf import settings
from django.http import HttpResponseForbidden
from django.middleware.csrf import get_token


# https://dan.lousqui.fr/legitimate-cross-site-request-a-cors-and-csrf-story-en.html

def csrf_header_middleware(get_response):
    def middleware(request):
        csrf_token = ""
        if "HTTP_COOKIE" in request.META:
            http_cookies = request.META['HTTP_COOKIE'].split("; ")
            for http_cookie in http_cookies:
                if http_cookie.startswith("csrftoken"):
                    csrf_token = http_cookie.split("=")[1]
        if csrf_token == "" or csrf_token == 'undefined':
            csrf_token = get_token(request)
        request.COOKIES['csrftoken'] = csrf_token
        request.META['HTTP_X_CSRFTOKEN'] = csrf_token
        response = get_response(request)
        # response.__setitem__("X-CSRFToken", csrf_token)
        return response
    return middleware


def react_header_middleware(get_response):
    def middleware(request):
        super_secret = ""
        if "REACT_SUPER_SECRET" not in request.META:
            print('key not present')
            return HttpResponseForbidden()
        super_secret = request.META.get("REACT_SUPER_SECRET")
        if super_secret != settings.REACT_SUPER_SECRET_KEY:
            print("keys do not match")
            return HttpResponseForbidden()
        else:
            return get_response(request)
    return middleware