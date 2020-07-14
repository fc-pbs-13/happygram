from django.shortcuts import render
from rest_framework import mixins
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.db.models import F
from posts.models import Post, Comment, Like
from posts.serializers import PostSerializer, CommentSerializer, LikeSerializer


class PostViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        if 'post_pk' in self.kwargs:
            post = get_object_or_404(Post, id=self.kwargs.get('post_pk'))

            serializer.save(
                user=self.request.user,
                post=post
            )
        # post_id=int(self.kwargs['post_pk']) request 믿을 수 x

        elif 'comment_pk' in self.kwargs:
            parent = get_object_or_404(Comment, id=self.kwargs.get('comment_pk'))

            serializer.save(
                user=self.request.user,
                parent=parent
            )


class LikeViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs.get('post_pk'))

        serializer.save(
            user=self.request.user,
            post=post
        )

        Post.objects.filter(id=post.id).update(like_count=F('like_count') + 1)

    def perform_destroy(self, instance):
        Post.objects.filter(id=instance.post_id).update(like_count=F('like_count') - 1)

        super().perform_destroy(instance)
