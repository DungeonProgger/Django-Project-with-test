from django.core.exceptions import PermissionDenied


def role_required(allowed_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Требуется авторизация")
            if request.user.role not in allowed_roles:
                raise PermissionDenied("Нет прав для выполнения операции")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
