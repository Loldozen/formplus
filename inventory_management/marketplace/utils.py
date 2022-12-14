from django.conf import settings
from jwt import decode as jwt_decode
from jwt import encode as jwt_encode
from jwt.exceptions import InvalidTokenError

from rest_framework import pagination, exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header


def generate_jwt_token(payload):
    """Generate authentication token."""
    return jwt_encode(payload, settings.JWT_SECRET_KEY, settings.JWT_ALGO)


class ExternalJWTAuthentication(BaseAuthentication):
    """Authentication class for jwt validation."""

    def authenticate(self, request):
        """Authenticate jwt token."""

        payload = {}
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'bearer':
            try:
                auth = request.headers.get('X-Authorization', None).split()
                if not auth[0].lower() == 'bearer':
                    msg = 'Invalid basic header 1.'
                    raise exceptions.AuthenticationFailed(msg)
            except AttributeError:
                msg = 'Invalid basic header 2.'
                raise exceptions.AuthenticationFailed(msg)
        if len(auth) == 1:
            msg = 'Invalid basic header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        if len(auth) > 2:
            msg = 'Invalid basic header. Credentials string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)
        token = auth[1]
        try:
            payload = jwt_decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGO])
        except InvalidTokenError:
            msg = 'Invalid token.'
            raise exceptions.AuthenticationFailed(msg)
        partner = payload.get('partner')
        if not partner or partner not in settings.AUTH_PARTNERS:
            raise exceptions.AuthenticationFailed('Invalid Token')

        return True, payload

class CustomPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'p'


def convert_order_state_to_int(state:str) -> int:
    if state.lower() == 'carted':
        return 0
    elif state.lower() == 'paid':
        return 1
    elif state.lower() == 'completed':
        return 2
    elif state.lower() == 'cancelled':
        return 3