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
        if csrf_token == "":
            csrf_token = get_token(request)
        request.COOKIES['csrftoken'] = csrf_token
        response = get_response(request)
        response.__setitem__("X-CSRFToken", csrf_token)
        return response
    return middleware
