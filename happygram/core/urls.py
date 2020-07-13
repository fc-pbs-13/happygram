from rest_framework.routers import SimpleRouter
from posts.views import PostViewSet, CommentNestedViewSet, CommentViewSet, LikeNestedViewSet
from profiles.views import ProfileViewSet
from users.views import UserViewSet
from rest_framework_nested import routers

router = SimpleRouter(trailing_slash=False)

router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

# post-comment
comment_router = routers.NestedSimpleRouter(router, r'posts', lookup='post')
# comment_router.register(r'comments', CommentNestedViewSet, basename='post_comment')
comment_router.register(r'comments', CommentViewSet, basename='post_comment')

# post-like
like_router = routers.NestedSimpleRouter(router, r'posts', lookup='post')
like_router.register(r'likes', LikeNestedViewSet, basename='post_like')

urlpatterns = router.urls + comment_router.urls + like_router.urls
