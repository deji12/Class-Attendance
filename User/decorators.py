from django.http import HttpResponseForbidden
from functools import wraps

def class_representative_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and getattr(user, 'is_class_representative', False):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You must be a class representative to access this view.")
    return _wrapped_view
