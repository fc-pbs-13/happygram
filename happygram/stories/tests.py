from datetime import timedelta

from dateutil.parser import parse
from django.utils import timezone
from model_bakery import baker
from munch import Munch
from rest_framework import status
from rest_framework.test import APITestCase
from core.temporaryimage import TempraryImageMixin
from relations.models import Relation
from stories.models import Story, StoryRead


class StoryTestCase(APITestCase, TempraryImageMixin):
    def setUp(self) -> None:
        self.users = baker.make('users.User', _quantity=3)
        self.stories = []

        for user in self.users:
            story = baker.make('stories.Story', user=user)
            self.stories.append(story)

        self.story = self.stories[0]
        # self.relation = baker.make('relations.Relation', from_user=self.users[0], to_user=self.users[1],
        #                            related_type=Relation.RelationChoice.follow)
        self.relation = baker.make('relations.Relation', from_user=self.users[2], to_user=self.users[1],
                                   related_type=Relation.RelationChoice.FOLLOW)
        self.relation = baker.make('relations.Relation', from_user=self.users[0], to_user=self.users[2],
                                   related_type=Relation.RelationChoice.FOLLOW)
        self.relation = baker.make('relations.Relation', from_user=self.users[1], to_user=self.users[2],
                                   related_type=Relation.RelationChoice.FOLLOW)
        self.user = self.users[0]

    def test_story_create(self):
        """ 스토리 생성"""
        data = {
            'image': self.temporary_image(),
            'caption': 'hi python!'
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/stories', data=data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['caption'], data['caption'])

    def test_story_update(self):
        """스토리 수정"""
        data = {
            'caption': "bye!"
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(f'/api/stories/{self.story.id}', data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['caption'], data['caption'])

    def test_story_destroy(self):
        """스토리 삭제 """
        self.client.force_authenticate(user=self.user)

        s = self.client.get(f'/api/stories/{self.story.id}')

        response = self.client.delete(f'/api/stories/{self.story.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Story.objects.filter(pk=self.story.id).exists())

    def test_story_list(self):
        """following user, my story 만 리스트"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/stories')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        my_followings = Relation.objects.filter(from_user=self.user).values('to_user')

        for r in response.data['results']:
            if r['user'] in my_followings:
                self.assertTrue(Story.objects.filter(user=r['user'], caption=r['caption']).exists())
            elif r['user'] == self.user:
                self.assertTrue(Story.objects.filter(user=r['user'], caption=r['caption']).exists())

    def test_story_time(self):
        """작성한지 24시간 이내에 스토리만 보임"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/stories')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        time_standard = timezone.now() - timedelta(days=1)
        for r in response.data['results']:
            date_time_obj = parse(r['created'])
            self.assertTrue(time_standard < date_time_obj)

    def test_story_read(self):
        """디테일로 조회한 스토리는 story_read model에 저장 -> id 반환"""
        # self.client.force_authenticate(user=self.user)
        #
        # baker.make('stories.StoryRead', user=self.user, story=self.story)
        #
        # response = self.client.get('/api/stories')
        #
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        #
        # for r in response.data['results']:
        #     if r['story_read_id']:
        #         self.assertTrue(StoryRead.objects.filter(user=self.user, id=r['story_read_id']).exists())

    def test_stroy_datail(self):
        baker.make('stories.StoryRead', story=self.story, user=self.user)
        # baker.make('stories.StoryRead', story=self.story, user=self.users[1])

        self.client.force_authenticate(user=self.users[1])

        response = self.client.get(f'/api/stories/{self.story.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_story = Munch(response.data)
        self.assertEqual(response_story.id, self.story.id)
        self.assertEqual(response_story.user, self.story.user.id)
        self.assertEqual(response_story.caption, self.story.caption)

    def test_story_read_list(self):
        baker.make('stories.StoryRead', story=self.story, user=self.user)

        self.client.force_authenticate(user=self.users[1])
        self.client.get(f'/api/stories/{self.story.id}')

        response = self.client.get(f'/api/stories/{self.story.id}/read')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        storyread = StoryRead.objects.filter(story_id=self.story.id).order_by('-id')

        self.assertEqual(len(response.data['results']), len(storyread))
        for response_data, response_obj in zip(response.data['results'], storyread):
            self.assertEqual(response_data['read_users']['user'], response_obj.user.id)
