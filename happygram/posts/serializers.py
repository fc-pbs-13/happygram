from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers
from posts.models import Post, Photo, Comment, Like
from rest_framework.validators import UniqueTogetherValidator


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('image',)


class RecursiveField(serializers.Serializer):
    """
    Self-referential field for MPTT.
    대댓글 작성에
    """

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, required=False)

    def validate(self, attrs):
        try:
            level = Comment.objects.get(pk=self.context['view'].kwargs['comment_pk']).level
        except:
            # 댓글인 경우
            return super().validate(attrs)

        # 대댓글인 경우 reply
        if level == 0:
            return super().validate(attrs)
        else:
            raise serializers.ValidationError('대댓글만 작성 가능')

    class Meta:
        model = Comment
        fields = ('id', 'post_id', 'parent', 'user_id', 'contents', 'level', 'children')


class CustomUniqueTogetherValidator(UniqueTogetherValidator):
    def enforce_required_fields(self, attrs, serializer):
        attrs['user_id'] = serializer.context['request'].user.id
        attrs['post_id'] = serializer.context['request'].parser_context['kwargs']['post_pk']
        super().enforce_required_fields(attrs, serializer)


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'post_id', 'user_id',)
        # # # validate할 때 user 데이터가 없어서 에러 발생 -> enforce_required_fields를 오버라이드해서 user와 함께 검사!
        validators = [
            CustomUniqueTogetherValidator(
                queryset=Like.objects.all(),
                fields=('post_id', 'user_id')
            )
        ]


class PostSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    _img = PhotoSerializer(many=True, read_only=True, source='img')
    img = serializers.ListField(child=serializers.ImageField(), write_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    user_like = serializers.SerializerMethodField()
    user_like_id = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'email', 'img', '_img', 'caption', 'created',
            'modified', 'comments', 'like_count', 'user_like',
            'user_like_id'
        )

    def create(self, validated_data):
        images = validated_data.pop('img')  # post 모델 안에 img 없음

        post = Post.objects.create(**validated_data)
        photo_list = []
        for image in images:
            photo_list.append(Photo(post=post, image=image))
        Photo.objects.bulk_create(photo_list)

        return post

    def get_user_like(self, obj):
        """request user가 post를 like 여부"""
        result = isinstance(self.context['request'].user, AnonymousUser)
        if result:
            return False
        return Like.objects.filter(post=obj, user=self.context['request'].user).exists()

    def get_user_like_id(self, obj):
        """request user가 post를 like했을 때 like_id -> delete할 때 필요 """
        try:
            like_id = Like.objects.get(post=obj, user=self.context['request'].user).id
        except:
            like_id = ""
        return like_id
