from django.conf import settings
from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from posts.views import PostViewSet, CommentViewSet, LikeViewSet, TagViewSet, CommentNestedViewSet, TaggedPostViewSet
from profiles.views import ProfileViewSet
from relations.views import RelationViewSet
from stories.views import StoryViewSet, StoryReadViewSet
from users.views import UserViewSet
from rest_framework_nested import routers

router = SimpleRouter(trailing_slash=False)

router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'likes', LikeViewSet)
router.register(r'relations', RelationViewSet)
router.register(r'stories', StoryViewSet)
router.register(r'tags', TagViewSet)

# post-comment-create
comment_router = routers.NestedSimpleRouter(router, r'posts', lookup='post')
comment_router.register(r'comments', CommentNestedViewSet, basename='post_comment')
comment_router.register(r'likes', LikeViewSet, basename='post_like')

# comment-reply-create
reply_router = routers.NestedSimpleRouter(router, r'comments', lookup='comment')
reply_router.register(r'reply', CommentNestedViewSet, basename='comment_reply')

# story-read-list
story_read_router = routers.NestedSimpleRouter(router, r'stories', lookup='story')
story_read_router.register(r'read', StoryReadViewSet, basename='story_read')

# tag name -post-list
tag_router = routers.NestedSimpleRouter(router, r'tags', lookup='tag')
tag_router.register(r'posts', TaggedPostViewSet, basename='tag_post')


urlpatterns = router.urls + comment_router.urls + reply_router.urls + tag_router.urls + story_read_router.urls

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
