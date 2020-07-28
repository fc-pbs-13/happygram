from django.utils import timezone
from rest_framework import mixins
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from datetime import datetime, timedelta

from core.pemissions import IsOwner
from relations.models import Relation
from stories.models import Story, StoryRead
from stories.serializers import StoryListSerializer, StoryDetailSerializer
from users.models import User
from django.db.models import Q


class StoryViewSet(ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StoryListSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        if self.action == 'list':
            # filter : 내가 팔로잉하는 유저의 id list
            sub_query = Relation.objects.filter(from_user=self.request.user,
                                                related_type=Relation.RelationChoice.FOLLOW).values('to_user')
            # related_query_name 사용
            # sub_query = User.objects.filter(Q(to_users_relation__from_user=self.request.user,
            #                                 to_users_relation__related_type=Relation.RelationChoice.follow) )

            time_standard = timezone.now() - timedelta(days=1)

            # filter : 24시간 이내 스토리 , 내가 작성 or my_following 작성
            queryset = Story.objects.filter(created__gt=time_standard).filter(
                Q(user__in=sub_query, ) | Q(user=self.request.user))
            return queryset
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        # request user와 현재 story pk 를 저장
        StoryRead.objects.create(user=self.request.user, story_id=kwargs['pk'])
        response = super().retrieve(request, *args, **kwargs)

        return response

    def paginate_queryset(self, queryset):
        # 모든 스토리
        page = super().paginate_queryset(queryset)
        # 내가 읽은 스토리 list
        self.story_read = {story_read.story_id: story_read.id for story_read in
                           StoryRead.objects.filter(user=self.request.user, story__in=page)}
        return page


class StoryReadViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = StoryRead.objects.all()
    serializer_class = StoryDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset().filter(story_id=self.kwargs.get('story_pk')).select_related('user__profile')
        return queryset
