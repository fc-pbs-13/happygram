from django.shortcuts import render
from rest_framework import mixins
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.db.models import F
from taggit.models import Tag
from taggit_serializer.serializers import TaggitSerializer

from core.pemissions import IsOwner
from posts.models import Post, Comment, Like
from posts.serializers import PostSerializer, CommentSerializer, LikeSerializer, UserLikeListSerializer, TagSerializer
from users.models import User


class PostViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  GenericViewSet):
    """post viewset"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwner]

    def paginate_queryset(self, queryset):
        # 모든 포스트
        page = super().paginate_queryset(queryset)
        # 해당 포스트의 좋아요중 내가 한것만
        self.like_dic = {like.post_id: like.id for like in Like.objects.filter(user=self.request.user, post__in=page)}
        return page

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Post.objects.prefetch_related('user').prefetch_related('img').prefetch_related('tags')
        return queryset


class TaggedPostViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    tag/{tag_name}/post
    post listview
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        # tags/{tag_name}/post -> safe
        if 'tag_pk' in self.kwargs:
            get_object_or_404(Tag, name=self.kwargs.get('tag_pk'))
            return super().get_queryset().filter(tags__name__icontains=self.kwargs['tag_pk']).distinct()


class TagViewSet(mixins.ListModelMixin, GenericViewSet):
    """tag_search"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        queryset = super().get_queryset()
        # query_params -> 태그 검색
        tag_search = self.request.query_params.get('tag', None)
        if tag_search is not None:
            queryset = queryset.filter(name__startswith=tag_search)
        else:  # query_params 없을 때
            raise MethodNotAllowed('no tag search')
        return queryset


class CommentViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    """comment viewset"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwner]


class CommentNestedViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    """post - comment list & create viewset"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        # Comment.objects.prefetch_related('parent__')
        queryset = super().get_queryset().filter(post=self.kwargs.get('post_pk')).prefetch_related('children__children')
        return queryset

    def perform_create(self, serializer):
        if 'post_pk' in self.kwargs:
            #  댓글인 경우
            post = get_object_or_404(Post, id=self.kwargs.get('post_pk'))

            serializer.save(
                user=self.request.user,
                post=post,
                parent=None
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
    permission_classes = [IsOwner]

    def get_queryset(self):
        if self.action == 'list':
            return super().get_queryset().filter(user=self.request.user).select_related('post__user').prefetch_related(
                'post__img')
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
