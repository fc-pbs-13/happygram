from django.contrib.auth.models import User
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate

from posts.serializers import LikeSerializer
from profiles.serializers import ProfileSerializer
from relations.models import Relation
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password')

    def create(self, validated_data):
        """ POST: 유저 회원가입 """
        user = User(
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UpdatePasswordSerializer(serializers.ModelSerializer):
    """update user password """

    class Meta:
        model = User
        fields = ('password',)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if user is None:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class FollowerSerializer(serializers.ModelSerializer):
    # 해당 유저 팔로워 리스트
    profile = ProfileSerializer(source='to_user.profile', read_only=True)

    class Meta:
        model = Relation
        fields = ('id', 'from_user', 'profile')


class FollowingSerializer(serializers.ModelSerializer):
    # 해당 유저의 팔로잉 리스트
    profile = ProfileSerializer(source='from_user.profile', read_only=True)

    class Meta:
        model = Relation
        fields = ('id', 'to_user', 'profile')


class BlockSerializer(serializers.ModelSerializer):
    # 해당 유저의 블록 리스트
    profile = ProfileSerializer(source='to_user.profile', read_only=True)

    class Meta:
        model = Relation
        fields = ('id', 'from_user', 'profile')
