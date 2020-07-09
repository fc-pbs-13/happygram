from rest_framework.routers import SimpleRouter
from posts.views import PostViewSet
from profiles.views import ProfileViewSet
from users.views import UserViewSet

router = SimpleRouter(trailing_slash=False)

router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'posts', PostViewSet)

urlpatterns = router.urls
