from rest_framework import serializers
from posts.models import Post, Photo


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'post_id', 'image')


class PostSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    img = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'email', 'img', 'caption', 'created', 'modified')

    def create(self, validated_data):
        images = self.context['request'].FILES
        post = Post.objects.create(**validated_data)

        for image in images.getlist('image'):
            Photo.objects.create(post=post, image=image)
        return post

    def save(self, **kwargs):
        return super().save(**kwargs)
