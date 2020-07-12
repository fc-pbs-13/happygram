from rest_framework.routers import SimpleRouter
from posts.views import PostViewSet, CommentNestedViewSet
from profiles.views import ProfileViewSet
from users.views import UserViewSet
from rest_framework_nested import routers

router = SimpleRouter(trailing_slash=False)

router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'posts', PostViewSet)

comment_router = routers.NestedSimpleRouter(router, r'posts', lookup='post')
comment_router.register(r'comments', CommentNestedViewSet, basename='post_comment')

urlpatterns = router.urls + comment_router.urls
