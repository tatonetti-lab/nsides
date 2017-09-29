from flask import redirect, request, session, url_for
from functools import wraps


def authenticated(fn):
    """Mark a route as requiring authentication."""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if not session.get('is_authenticated'):
            return redirect(url_for('login', next=request.url))

        if request.path == '/logout':
            return fn(*args, **kwargs)

        return fn(*args, **kwargs)
    return decorated_function
