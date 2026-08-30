from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def admin_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is an admin.
    Redirects to admin login if the user is not authenticated or not an admin.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in with administrator privileges to access the dashboard.")
            return redirect('admin_login')
        if not getattr(request.user, 'is_admin', False):
            messages.error(request, "Access denied. Administrator privileges required.")
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
