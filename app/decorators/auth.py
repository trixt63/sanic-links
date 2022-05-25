from functools import wraps
import jwt

from config import Config 
from app.hooks.error import ApiUnauthorized


def check_token(request):
    token = request.token
    if not token:
        return False

    try:
        jwt.decode(
            token, Config.SECRET_KEY, algorithms=["HS256"]
        )
    except jwt.exceptions.InvalidTokenError:
        return False
    else:
        return True


def protected(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authenticated = check_token(request)

            if is_authenticated:
                response = await f(request, *args, **kwargs)
                return response
            else:
                raise ApiUnauthorized("You are unauthorized.")

        return decorated_function

    return decorator(wrapped)
 