from django.utils import timezone

from django.shortcuts import render
from rest_framework import status, serializers
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.fields import EmailField
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.pemissions import UserIsOwner
from relations.models import Relation
from users.models import User
from users.serializers import UserSerializer, CustomAuthTokenSerializer, UpdatePasswordSerializer, FollowerSerializer, \
    FollowingSerializer, BlockSerializer

from time import sleep
from django.core.cache import cache
from rest_framework.decorators import action
from rest_framework.response import Response


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserIsOwner]

    authentication_classes = [] #todo locust testc용

    def get_serializer_class(self):
        if self.action == 'follow':
            return FollowerSerializer
        elif self.action == 'following':
            return FollowingSerializer
        elif self.action == 'block':
            return BlockSerializer
        else:
            return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ['login', 'create', 'locust_test']:
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        if self.action == 'follow':
            return Relation.objects.filter(from_user=self.kwargs['pk'],
                                           related_type=Relation.RelationChoice.FOLLOW).select_related(
                'to_user__profile')
        elif self.action == 'following':
            return Relation.objects.filter(to_user=self.kwargs['pk'],
                                           related_type=Relation.RelationChoice.FOLLOW).select_related(
                'from_user__profile')
        elif self.action == 'block':
            return Relation.objects.filter(from_user=self.request.user,
                                           related_type=Relation.RelationChoice.BLOCK).select_related(
                'to_user__profile')
        else:
            return super().get_queryset()

    @action(methods=['post'], detail=False)
    def login(self, request, *args, **kwargs):
        serializer = CustomAuthTokenSerializer(data=request.data,
                                               context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        # 유저 로그인하면 캐시 ttl 설정
        key = user.id
        val = cache.get(key)

        if val is None:
            sleep(3)
            val = ""
            cache.set(key, val, 10)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)

    @action(methods=['delete'], detail=False)
    def logout(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        key = 'token_key'
        cache.delete(key)
        val = cache.get(key)

        return Response({'cache': val}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['patch'], detail=False)
    def update_password(self, request, *args, **kwargs):
        """request token user의 password를 바꾼다 """
        instance = self.request.user
        serializer = UpdatePasswordSerializer(instance, data=request.data, context={'request': request}, )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True)
    def follow(self, request, *args, **kwargs):
        # 해당 유저의 팔로우 리스트
        return super().list(request, *args, **kwargs)

    @action(detail=True)
    # 해당 유저를 팔로우하는 리스
    def following(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False)
    def block(self, request, *args, **kwargs):
        # 해당 유저의 팔로우 리스트
        return super().list(request, *args, **kwargs)

    @action(detail=False)
    def locust_test(self, request, *args, **kwargs):
        return Response()
