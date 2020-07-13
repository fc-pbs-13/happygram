from django.shortcuts import render
from rest_framework import mixins
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from posts.models import Post, Comment, Like
from posts.serializers import PostSerializer, CommentSerializer, LikeSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentNestedViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'])

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            post_id=int(self.kwargs['post_pk']),
        )


class CommentViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = CommentSerializer

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs.get('post_pk'))

        serializer.save(
            user=self.request.user,
            post=post)
        # post_id=int(self.kwargs['post_pk']),


class LikeNestedViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def get_queryset(self):
        return Like.objects.filter(post_id=self.kwargs['post_id'])

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            post_id=int(self.kwargs['post_pk']),
        )
