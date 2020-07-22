from django.shortcuts import render
from rest_framework import mixins
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.db.models import F
from posts.models import Post, Comment, Like
from posts.serializers import PostSerializer, CommentSerializer, LikeSerializer, UserLikeListSerializer
from users.models import User


class PostViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  GenericViewSet):
    """post viewset"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def paginate_queryset(self, queryset):
        # 모든 포스트
        page = super().paginate_queryset(queryset)
        # 해당 포스트의 좋아요중 내가 한것만
        self.like_dic = {like.post_id: like.id for like in Like.objects.filter(user=self.request.user, post__in=page)}
        return page

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    """comment viewset"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        if 'post_pk' in self.kwargs:
            #  댓글인 경우
            post = get_object_or_404(Post, id=self.kwargs.get('post_pk'))

            serializer.save(
                user=self.request.user,
                post=post
            )

        elif 'comment_pk' in self.kwargs:
            # 대댓글인 경우
            parent = get_object_or_404(Comment, id=self.kwargs.get('comment_pk'))

            serializer.save(
                user=self.request.user,
                parent=parent
            )


class LikeViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    """like viewset"""
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def get_queryset(self):
        if self.action == 'list':
            return super().get_queryset().filter(user=self.request.user).select_related('post')
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == 'list':
            return UserLikeListSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs.get('post_pk'))

        serializer.save(
            user=self.request.user,
            post=post
        )
