from django.utils import timezone
from rest_framework.viewsets import ModelViewSet
from datetime import datetime, timedelta
from relations.models import Relation
from stories.models import Story, StoryRead
from stories.serializers import StorySerializer
from users.models import User
from django.db.models import Q


class StoryViewSet(ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer

    def get_queryset(self):
        # filter : 내가 팔로잉하는 유저의 id list
        sub_query = Relation.objects.filter(Q(from_user=self.request.user,
                                              related_type=Relation.RelationChoice.follow)).values('to_user')
        # related_query_name 사용
        # sub_query = User.objects.filter(Q(to_users_relation__from_user=self.request.user,
        #                                 to_users_relation__related_type=Relation.RelationChoice.follow) )

        # filter : sub_query and 24시간 이내 스토리 ,내가 작성한 스토리
        time_standard = timezone.now() - timedelta(hours=24)
        queryset = Story.objects.filter(
            Q(user__in=sub_query, created__gt=time_standard) | Q(user=self.request.user))

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        # request user와 현재 story pk 를 저장
        StoryRead.objects.create(user=self.request.user, story_id=kwargs['pk'])
        return super().retrieve(request, *args, **kwargs)

    def paginate_queryset(self, queryset):
        # 모든 스토리
        page = super().paginate_queryset(queryset)
        # 내가 읽은 스토리 list
        self.story_read = {story_read.story.id: story_read.id for story_read in
                           StoryRead.objects.filter(user=self.request.user, story__in=page)}
        return page