from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.pemissions import RelationIsOwner
from relations.models import Relation
from relations.serializers import RelationSerializer


class RelationViewSet(ModelViewSet):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
    permission_classes = [RelationIsOwner]

    def perform_create(self, serializer):

        serializer.save(from_user=self.request.user)
