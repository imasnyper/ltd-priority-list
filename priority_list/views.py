from django.http import JsonResponse
from django.middleware.csrf import get_token


def csrf(request):
    token = get_token(request)
    response = JsonResponse({'csrftoken': token})
    print(token)
    return response
