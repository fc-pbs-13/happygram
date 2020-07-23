from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from taggit.models import Tag

from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from posts.models import Post, Photo, Comment, Like
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.generics import get_object_or_404


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'image',)


class RecursiveField(serializers.Serializer):
    """
    Self-referential field for MPTT.
    대댓글 작성에
    """

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True, required=False)  # 대댓글이 parent 댓글에 붙는다

    def validate(self, attrs):
        if 'comment_pk' in self.context['view'].kwargs:
            # 대댓글인 경우
            comment = get_object_or_404(Comment, id=self.context['view'].kwargs['comment_pk'])
            if comment.level != 0:
                # 대댓글의 부모가 0이 아니면 에러
                raise ValidationError
        return attrs  # 댓글인 경우

    class Meta:
        model = Comment
        fields = ('id', 'post_id', 'parent', 'user_id', 'contents', 'level', 'children')
        ordering = ('-id',)


class CustomUniqueTogetherValidator(UniqueTogetherValidator):
    def enforce_required_fields(self, attrs, serializer):
        attrs['user_id'] = serializer.context['request'].user.id
        attrs['post_id'] = serializer.context['request'].parser_context['kwargs']['post_pk']
        super().enforce_required_fields(attrs, serializer)


class PostSerializer(TaggitSerializer, serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    _img = PhotoSerializer(many=True, read_only=True, source='img')
    img = serializers.ListField(child=serializers.ImageField(), write_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    user_like_id = serializers.SerializerMethodField()
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Post
        fields = (
            'id', 'email', 'img', '_img', 'caption', 'created',
            'modified', 'comments', 'like_count', 'user_like_id', 'tags'
        )
        extra_kwargs = {'caption': {'required': False}}

    def create(self, validated_data):
        images = validated_data.pop('img')  # post 모델 안에 img 없음
        post = Post.objects.create(**validated_data)
        photo_list = []
        for image in images:
            photo_list.append(Photo(post=post, image=image))
        Photo.objects.bulk_create(photo_list)

        return post

    def get_user_like_id(self, obj):
        """ request user가 like한 포스트들은 like_id가 보인다   """
        if self.context['view'].action == 'list':
            like_id = self.context['view'].like_dic.get(obj.id)
            return like_id
        return None


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


class LikePostSerializer(serializers.ModelSerializer):
    """like post 생성/ 삭제"""
    email = serializers.EmailField(source='user.email', read_only=True)
    _img = PhotoSerializer(many=True, read_only=True, source='img')

    class Meta:
        model = Post
        fields = (
            'id', 'email', '_img',
        )


class UserLikeListSerializer(serializers.ModelSerializer):
    """user가 like한 post list"""
    post = LikePostSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'post')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name',)
