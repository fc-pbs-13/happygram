import pytz
from django.utils import timezone
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import datetime, timedelta
from relations.models import Relation
from stories.models import Story, StoryRead


class StoryTestCase(APITestCase):
    def setUp(self) -> None:
        self.users = baker.make('users.User', _quantity=3)
        self.stories = []
        self.stories.append(baker.make('stories.Story', user=self.users[0]))
        self.stories.append(baker.make('stories.Story', user=self.users[1]))
        self.stories.append(baker.make('stories.Story', user=self.users[2]))
        self.story = self.stories[0]
        # self.relation = baker.make('relations.Relation', from_user=self.users[0], to_user=self.users[1],
        #                            related_type=Relation.RelationChoice.follow)
        self.relation = baker.make('relations.Relation', from_user=self.users[2], to_user=self.users[1],
                                   related_type=Relation.RelationChoice.follow)
        self.relation = baker.make('relations.Relation', from_user=self.users[0], to_user=self.users[2],
                                   related_type=Relation.RelationChoice.follow)
        self.relation = baker.make('relations.Relation', from_user=self.users[1], to_user=self.users[2],
                                   related_type=Relation.RelationChoice.follow)
        self.user = self.users[0]

    def temporary_image(self):
        """
        임시 이미지 파일
        """
        import tempfile
        from PIL import Image

        image = Image.new('RGB', (10, 10))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file, 'jpeg')
        tmp_file.seek(0)
        return tmp_file

    def test_story_create(self):
        """ 스토리 생성"""
        data = {
            'image': self.temporary_image(),
            'caption': 'hi python!'
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/stories', data=data)

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

        self.assertFalse(Story.objects.filter(pk=self.story.id))

    def test_story_list(self):
        """following user, my story 만 리스트"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/stories')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for r in response.data['results']:
            if r['user'] in Relation.objects.filter(from_user=self.user).values('to_user') or r['user'] == self.user:
                self.assertTrue(Story.objects.filter(user=r['user'], caption=r['caption']).exists())

    def test_story_time(self):
        """작성한지 24시간 이내에 스토리만 보임"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/stories')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        time_standard = timezone.now() - timedelta(hours=24)
        for r in response.data['results']:
            date_time_obj = datetime.strptime(r['created'], '%Y-%m-%dT%H:%M:%S.%fZ')
            story_time = pytz.utc.localize(date_time_obj)
            self.assertTrue(story_time > time_standard)

    def test_story_read(self):
        """디테일로 조회한 스토리는 story_read model에 저장 -> id 반환"""
        self.client.force_authenticate(user=self.user)

        baker.make('stories.StoryRead', user=self.user, story=self.story)

        response = self.client.get('/api/stories')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for r in response.data['results']:
            if r['story_read_id']:
                self.assertTrue(StoryRead.objects.filter(user=self.user, id=r['story_read_id']).exists())
