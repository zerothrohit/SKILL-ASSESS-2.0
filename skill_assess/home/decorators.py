from functools import wraps
from django.http import HttpResponseForbidden

def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to access this page.")
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view