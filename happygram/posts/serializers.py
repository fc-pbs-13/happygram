from rest_framework import serializers
from posts.models import Post, Photo, Comment


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'post_id', 'image')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'post_id', 'parent', 'user_id', 'contents')


class PostSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    img = PhotoSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'email', 'img', 'caption', 'created', 'modified', 'comments')

    def create(self, validated_data):
        images = self.context['request'].FILES
        post = Post.objects.create(**validated_data)

        for image in images.getlist('image'):
            Photo.objects.create(post=post, image=image)
        return post

    def save(self, **kwargs):
        return super().save(**kwargs)
