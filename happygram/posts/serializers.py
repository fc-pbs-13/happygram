from django.contrib.auth.models import AnonymousUser
from django.db.models import F
from rest_framework import serializers
from posts.models import Post, Photo, Comment, Like
from rest_framework.validators import UniqueTogetherValidator


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


class PostSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    _img = PhotoSerializer(many=True, read_only=True, source='img')
    img = serializers.ListField(child=serializers.ImageField(), write_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    user_like_id = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'email', 'img', '_img', 'caption', 'created',
            'modified', 'comments', 'like_count', 'user_like_id'
        )

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
        like_id = self.context['view'].like_dic.get(obj.id)
        return like_id


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
    email = serializers.EmailField(source='user.email', read_only=True)
    _img = PhotoSerializer(many=True, read_only=True, source='img')

    class Meta:
        model = Post
        fields = (
            'id', 'email', '_img',
        )


class UserLikeListSerializer(serializers.ModelSerializer):
    like_post = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Like
        fields = ('id', 'like_post', 'user')

    def get_like_post(self, obj):
        return LikePostSerializer(obj.post).data
