import functools
from tornado.web import HTTPError
import base64
from cooka.common import consts


def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if consts.AUTHENTICATION is not None:
            auth_header = self.request.headers.get('Authorization', None)
            if auth_header is not None:
                auth_mode, auth_base64 = auth_header.split(' ', 1)
                assert auth_mode == 'Basic'
                auth_username, auth_password = str(base64.b64decode(auth_base64.encode(encoding="utf-8")), "utf-8").split(':', 1)
                if auth_username == consts.USER_NAME and auth_password == consts.TOKEN:
                    return method(self, *args, **kwargs)
                else:
                    raise HTTPError(401)
            else:
                raise HTTPError(401)
        else:
            # No authentication
            return method(self, *args, **kwargs)
    return wrapper
