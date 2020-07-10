from model_bakery import baker
from munch import Munch
from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Post
from users.models import User


class PostTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(email="abc@abc.com", password="1234")

    def test_post_create(self):
        """"포스트 생성"""
        data = {
            'caption': 'hi~~~~~~!!!!',
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/posts', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        post_response = Munch(response.data)
        self.assertTrue(post_response.id)
        self.assertEqual(post_response.caption, data['caption'])

    def test_post_list(self):
        """"포스트 리스트"""
        # 데이터 만들기
        self.users = baker.make('users.User', _quantity=3)
        self.posts = []
        for user in self.users:
            self.posts += baker.make('posts.Post', _quantity=3, caption='hello bye', user=user)
        self.user = self.users[0]
        #

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/posts')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 페이지 네이션할 때 response.data['result']
        for post_response, post in zip(response.data, self.posts):
            self.assertEqual(post_response['caption'], post.caption)
            self.assertEqual(post_response['email'], post.user.email)

    def test_post_detail(self):
        """"포스트 디테일"""
        self.client.force_authenticate(user=self.user)
        self.post = Post.objects.create(caption="good bye.. ", user_id=self.user.id)

        response = self.client.get(f'/api/posts/{self.post.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        post_response = Munch(response.data)
        self.assertTrue(post_response.id)
        self.assertEqual(post_response.caption, self.post.caption)

    def test_post_update(self):
        """포스트 업데이"""
        self.post = Post.objects.create(caption="good bye.. ", user_id=self.user.id)

        prev_caption = self.post.caption
        data = {
            'caption': 'hello world'
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(f'/api/posts/{self.post.id}', data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        post_response = Munch(response.data)
        self.assertEqual(post_response.caption, data['caption'])
        self.assertNotEqual(post_response.caption, prev_caption)

    def test_post_delete(self):
        """포스트 삭제 """
        self.post = Post.objects.create(caption="good bye.. ", user_id=self.user.id)

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/posts/{self.post.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.filter(pk=self.post.id).count(), 0)


