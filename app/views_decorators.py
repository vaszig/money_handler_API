import json

from django.http import JsonResponse

from .models import Budget


def allowed_method(method): 
    """Decorator for checking the method of the request."""

    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if method == 'GET':
                if request.method == 'GET':
                    return func(request, *args, **kwargs)
                return JsonResponse({'message': 'Method not allowed'}, status=405)
            elif method == 'POST':
                if request.method == 'POST':
                    return func(request, *args, **kwargs)
                return JsonResponse({'message': 'Method not allowed'}, status=405)
        return wrapper
    return decorator


def parse_request_args(form):
    """Decorator for checking that new data from request can be converted to json and required fields are given."""

    def decorator(func):
        def wrapper(request, *args, **kwargs):    
            try:
                loaded_data = json.loads(request.body)
            except json.decoder.JSONDecodeError:
                return JsonResponse({'message': 'failed to load json data'}, status=400)
            for field in form.base_fields.keys():
                if field not in loaded_data:
                    return JsonResponse({'message': 'wrong or missing fieldnames'}, status=400)
            return func(request, loaded_data, *args, **kwargs)
        return wrapper
    return decorator


def parse_request_dates(form):
    """Decorator for checking dates from request."""
    
    def decorator(func):
        def wrapper(request, category, *args, **kwargs):
            for field in form.base_fields.keys():
                if field not in request.GET:
                    return JsonResponse({'message': 'wrong or missing fieldnames'}, status=400)
            return func(request, category, *args, **kwargs)
        return wrapper
    return decorator
