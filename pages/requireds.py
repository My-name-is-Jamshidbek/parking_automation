from django.http import HttpResponseNotFound


def staff_member_required_or_404(view_func):
    """Decorator that wraps the staff_member_required decorator to return 404."""
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseNotFound('Not found')

    return _wrapped_view
