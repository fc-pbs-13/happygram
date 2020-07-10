from rest_framework import serializers

from posts.models import Post


class PostSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Post
        fields = ('images', 'caption', 'date', 'id', 'email')




