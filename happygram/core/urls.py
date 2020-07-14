from rest_framework.routers import SimpleRouter
from posts.views import PostViewSet, CommentViewSet, LikeViewSet
from profiles.views import ProfileViewSet
from users.views import UserViewSet
from rest_framework_nested import routers

router = SimpleRouter(trailing_slash=False)

router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'likes', LikeViewSet)

# post-comment-create
comment_router = routers.NestedSimpleRouter(router, r'posts', lookup='post')
comment_router.register(r'comments', CommentViewSet, basename='post_comment')

# post-like-create
like_router = routers.NestedSimpleRouter(router, r'posts', lookup='post')
like_router.register(r'likes', LikeViewSet, basename='post_like')

urlpatterns = router.urls + comment_router.urls + like_router.urls
