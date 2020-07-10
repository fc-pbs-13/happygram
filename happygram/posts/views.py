from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from posts.models import Post
from posts.serializers import PostSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        l = []
        l.append(self.request.FILES['images'])
        serializer.save(user=self.request.user, images=l)

