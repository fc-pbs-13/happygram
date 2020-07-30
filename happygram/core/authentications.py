from django.core.cache import cache
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from django.utils.translation import gettext_lazy as _


class CustomTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        key = token.user_id
        val = cache.get(key)
        if val is None:
            token.delete()
            raise exceptions.AuthenticationFailed(_('캐시 삭제됨 다시 로그인하세요'))
        return token.user, token
