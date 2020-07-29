from model_bakery import baker
from munch import Munch
from rest_framework import status
from rest_framework.test import APITestCase
from taggit.models import Tag

from core.temporaryimage import TempraryImageMixin
from posts.models import Post, Comment, Like
from users.models import User


class PostTestCase(APITestCase, TempraryImageMixin):
    def setUp(self) -> None:
        self.user = baker.make('users.User')
        self.posts = []
        self.post = baker.make('posts.Post', user=self.user)
        self.posts.append(self.post)

    def test_post_create(self):
        """"포스트 생성"""
        image_test = [self.temporary_image(), self.temporary_image()]
        data = {
            # 'caption': 'hi~~~~~~!!!!'
            'img': image_test,
            # 'tags': '["dfdf","dfdf"]'
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/posts', data=data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        post_response = Munch(response.data)
        # print(response.data)
        self.assertTrue(post_response.id)
        self.assertEqual(len(post_response._img), len(image_test))
        # self.assertEqual(post_response.caption, data['caption'])

    def test_post_list(self):
        """"포스트 리스트"""
        self.posts += baker.make('posts.Post', _quantity=2, user=self.user)
        self.user2 = baker.make('users.User')
        # self.user2 = User.objects.create(email="hello@pl.com", password="1234")

        # self.user로 like post 생성 - 1번째 post
        self.client.force_authenticate(user=self.user)
        response_like = self.client.post(f'/api/posts/{self.post.id}/likes')

        request_user = self.user  # request_user를 user or user2로 테스트
        self.client.force_authenticate(user=request_user)
        response = self.client.get('/api/posts')
        self.fail()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for post_response, post in zip(response.data['results'], self.posts[::-1]):
            self.assertEqual(post_response['caption'], post.caption)
            self.assertEqual(post_response['email'], post.user.email)
            if post_response['user_like_id']:  # like 없는 post 있을 수 잇다
                self.assertEqual(post_response['user_like_id'], post.post_like.get(user=request_user).id)

    def test_tag_list(self):
        """태그 검색"""
        self.post.tags.add("python", "java", "ruby", "noja")
        post2 = baker.make('posts.Post')
        post2.tags.add("java2", "java0", "node")

        self.client.force_authenticate(user=self.user)
        search = "no"
        response = self.client.get(f'/api/tags?tag={search}')
        # comment
        # todo 태그 생성 test
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        searchable_tags = ['noja', 'node']  # search 결과 태그 리스트
        for r in response.data['results']:
            self.assertTrue(r['name'] in searchable_tags)

    def test_tag_list_no_search(self):
        """/api/tags -> method not allowed"""
        self.post.tags.add("python", "java", "ruby", "noja")

        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/tags')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_move_tag_post(self):
        """태그를 가진 포스트 리스트"""
        self.client.force_authenticate(user=self.user)

        self.post.tags.add("python", "ruby", "noja")
        posts = baker.make('posts.Post', _quantity=2)
        posts[0].tags.add("java2", "java", "node")
        posts[1].tags.add("javaq", "hi")

        tag_name = "java" # 없는 태그 검색시 404

        response = self.client.get(f'/api/tags/{tag_name}/posts')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 태그네임을 포함하는 포스트 query_set
        # post_qs = Post.objects.filter(tags__name__icontains=tag_name).order_by('-id').distinct()
        # static하게!
        post_qs = posts
        self.assertEqual(len(response.data['results']), len(post_qs))

        for r, post in zip(response.data['results'], post_qs[::-1]):
            self.assertEqual(r['id'], post.id)

    def test_post_update(self):
        """포스트 업데이트"""
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

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(f'/api/posts/{self.post.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.filter(pk=self.post.id).count(), 0)


class CommentTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = baker.make('users.User')
        self.post = baker.make('posts.Post', user=self.user)
        self.comments = baker.make('posts.Comment', _quantity=2, post=self.post, user=self.user,
                                   level=0)  # level = 0 -> 댓글
        self.comment = self.comments[0]

    def test_comment_list(self):
        self.reply = Comment.objects.create(user=self.user, parent=self.comments[0])
        self.reply1 = Comment.objects.create(user=self.user, parent=self.comments[1])
        self.reply1 = Comment.objects.create(user=self.user, parent=self.comments[1])
        self.post1 = baker.make('posts.Post', user=self.user)
        test = Comment.objects.create(user=self.user, post=self.post1)

        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/api/posts/{self.post.id}/comments')

        for r, c in zip(response.data['results'], self.comments[::-1]):
            self.assertEqual(r['id'], c.id)
            for reply_res, reply_obj in zip(r['children'], c.children.all()):
                self.assertEqual(reply_res['id'], reply_obj.id)

    def test_comment_create(self):
        """댓글 생성"""
        data = {
            'contents': 'hi~~~~~~!!!!',
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(f'/api/posts/{self.post.id}/comments', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        post_response = Munch(response.data)
        self.assertTrue(post_response.id)
        self.assertEqual(post_response.contents, data['contents'])
        self.assertEqual(post_response.post_id, self.post.id)
        self.assertEqual(post_response.user_id, self.user.id)

    def test_comment_update(self):
        """댓글 수정"""

        self.client.force_authenticate(user=self.user)

        data = {
            'contents': 'hi~~~~~~!!!!',
        }
        response = self.client.patch(f'/api/comments/{self.comment.id}', data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment_response = Munch(response.data)
        self.assertEqual(comment_response.contents, data['contents'])
        self.assertNotEqual(comment_response.contents, self.comment.contents)

    def test_comment_destroy(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/comments/{self.comment.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(pk=self.comment.id).exists())

    def test_reply_create(self):
        data = {
            'contents': 'reply!!!!!!!!!!!!!!!!',
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/comments/{self.comment.id}/reply', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        post_response = Munch(response.data)
        self.assertTrue(post_response.id)
        self.assertEqual(post_response.contents, data['contents'])
        self.assertEqual(post_response.user_id, self.user.id)

    def test_reply_level(self):
        data = {
            'contents': 'reply!!!!!!!!!!!!!!!!',
        }
        self.client.force_authenticate(user=self.user)

        response_success = self.client.post(f'/api/comments/{self.comment.id}/reply', data=data)

        data = {'contents': " 대대댓글은 no! "}
        response_fail = self.client.post(f"/api/comments/{response_success.data['id']}/reply", data=data)

        self.assertEqual(response_fail.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response_success.data['level'], 1)  # 댓글의 레벨이 1인 경우 이 댓글에 대댓글을 남길 수 없음


class PostLikeTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = baker.make('users.User')
        self.post = baker.make('posts.Post', user=self.user)

    def test_like_duplicate(self):
        self.client.force_authenticate(user=self.user)

        Like.objects.create(post=self.post, user=self.user)

        response = self.client.post(f'/api/posts/{self.post.id}/likes')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_like_count_create(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(f'/api/posts/{self.post.id}/likes')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Post.objects.get(pk=self.post.id).like_count, 1)

    def test_like_count_decrease(self):
        self.client.force_authenticate(user=self.user)

        post = baker.make('posts.Post', user=self.user, like_count=9)

        like = baker.make('posts.Like', post=post, user=self.user)  # like.id로 삭제

        self.assertEqual(Post.objects.get(pk=post.pk).like_count, 10)

        response = self.client.delete(f'/api/likes/{like.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(post.like_count, 9)

    def test_like_destroy(self):
        self.client.force_authenticate(user=self.user)

        response_create = self.client.post(f'/api/posts/{self.post.id}/likes')

        self.assertTrue(Like.objects.filter(post=self.post, user=self.user).exists())

        response = self.client.delete(f"/api/likes/{response_create.data['id']}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Like.objects.filter(post=self.post, user=self.user).exists())

    def test_like_create(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(f'/api/posts/{self.post.id}/likes')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['post_id'], self.post.id)
        self.assertEqual(response.data['user_id'], self.user.id)

    def test_user_like_get(self):
        """user's post-like list"""

        self.user1 = baker.make('users.User')
        self.post1 = baker.make('posts.Post', user=self.user)

        baker.make('posts.Like', post=self.post, user=self.user)
        baker.make('posts.Like', post=self.post1, user=self.user)
        baker.make('posts.Like', post=self.post, user=self.user1)

        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/likes')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for r in response.data['results']:
            # like objects에 response post.pk , user 조건을 만족하는지
            self.assertTrue(Like.objects.filter(post=r['post']['id'], user=self.user).exists())
