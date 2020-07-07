from rest_framework.routers import SimpleRouter

from users.views import UserViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
# router.register(r'profiles', ProfileViewSet)
urlpatterns = router.urls
