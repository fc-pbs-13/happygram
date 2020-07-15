from rest_framework import serializers

from relations.models import Relation


class RelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = ('id', 'to_user', 'related_type', 'from_user')
        read_only_fields = ('from_user',)
