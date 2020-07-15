from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from relations.models import Relation
from relations.serializers import RelationSerializer


class RelationViewSet(ModelViewSet):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)
