from rest_framework.routers import SimpleRouter

from users.views import UserViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r'users', UserViewSet)

urlpatterns = router.urls