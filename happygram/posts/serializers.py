from rest_framework import serializers

from posts.models import Post


class PostSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Post
        fields = ('images', 'user', 'caption', 'date', 'id', 'email')
