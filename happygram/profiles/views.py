from django.shortcuts import render
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from profiles.models import Profile
from profiles.serializers import ProfileSerializer


class ProfileViewSet(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     GenericViewSet):

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
