from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from relations.models import Relation


class CustomUniqueTogetherValidator(UniqueTogetherValidator):
    def enforce_required_fields(self, attrs, serializer):
        attrs['from_user'] = serializer.context['request'].user.id
        attrs['to_user'] = serializer.context['request'].data['to_user']
        super().enforce_required_fields(attrs, serializer)


class RelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = ('id', 'to_user', 'related_type', 'from_user')
        read_only_fields = ('from_user',)
        validators = [
            CustomUniqueTogetherValidator(
                queryset=Relation.objects.all(),
                fields=('from_user', 'to_user')
            )
        ]