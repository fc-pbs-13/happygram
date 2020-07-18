from model_bakery import baker
from munch import Munch
from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Post, Comment, Like
from users.models import User


class PostTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = baker.make('users.User')
        self.posts = []
        self.post = baker.make('posts.Post', user=self.user)
        self.posts.append(self.post)

    def temporary_image(self):
        """
        임시 이미지 파일
        """
        import tempfile
        from PIL import Image
        image = Image.new('RGB', (1, 1))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file, 'jpeg')
        tmp_file.seek(0)
        return tmp_file

    def test_post_create(self):
        """"포스트 생성"""
        image_test = [self.temporary_image(), self.temporary_image()]
        data = {
            'caption': 'hi~~~~~~!!!!',
            'img': image_test
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/posts', data=data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        post_response = Munch(response.data)
        self.assertTrue(post_response.id)
        self.assertEqual(len(post_response._img), len(image_test))
        self.assertEqual(post_response.caption, data['caption'])

    def test_post_comment(self):
        """댓글 parent - children"""
        # self.comments = baker.make('posts.Comment', _quantity=2, post=self.post, user=self.user, level=0)
        comment_a = Comment.objects.create(user=self.user, post=self.post)
        comment_b = Comment.objects.create(user=self.user, post=self.post)
        # self.reply = Comment.objects.create(user=self.user, parent=comment_a)
        # self.reply1 = Comment.objects.create(user=self.user, parent=comment_b)
        # Comment.objects.create(user=self.user, parent=comment_a)
        # Comment.objects.create(user=self.user, parent=comment_b)

        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/posts')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for comment in self.post.comments.all():
            print('comment:', comment.id, comment.tree_id, comment.lft)
            for child in comment.children.all():
                print('  child:', child.id, child.tree_id, child.lft)

        # print(response.content)
        for post in response.data['results']:
            for comment in post['comments']:
                print('comment:', comment['id'])
                for child in comment['children']:
                    print('  child:', child['id'])
        self.fail()

        for post in response.data['results']:
            print('len', len(post['comments']), len(self.comments))
            for response_comment, comment in zip(post['comments'], self.comments):
                print(response_comment['id'], comment.id)
                # self.assertEqual(response_comment['contents'], comment.contents)
                # for response_reply , reply in zip(response_comment, comment.children.all()):
                #     print("ㅎㅎㅎ과연!",response_reply)
                #     print("어딨냐 ",reply)
                # self.assertEqual(response_reply, reply)

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

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for post_response, post in zip(response.data['results'], self.posts[::-1]):
            self.assertEqual(post_response['caption'], post.caption)
            self.assertEqual(post_response['email'], post.user.email)
            if post_response['user_like_id']:  # like 없는 post 있을 수 잇다
                self.assertEqual(post_response['user_like_id'], post.post_like.get(user=request_user).id)

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
        self.comment = baker.make('posts.Comment', post=self.post, user=self.user, level=0)  # level = 0 -> 댓글

    def test_comment_create(self):
        """댓글 생성"""
        data = {
            'contents': 'hi~~~~~~!!!!',
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.post(f'/api/posts/{self.post.id}/comments', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
        self.assertEqual(Post.objects.filter(pk=self.comment.id).count(), 0)

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

        like = baker.make('posts.Like', post=post, user=self.user)

        response = self.client.delete(f'/api/likes/{like.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(post.like_count, 9)

    def test_like_destroy(self):
        self.client.force_authenticate(user=self.user)

        response_create = self.client.post(f'/api/posts/{self.post.id}/likes')

        response = self.client.delete(f"/api/likes/{response_create.data['id']}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.get(pk=self.post.id).like_count, 0)

    def test_like_create(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(f'/api/posts/{self.post.id}/likes')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_like_get(self):
        self.user1 = baker.make('users.User')
        self.post1 = baker.make('posts.Post', user=self.user)
        
        like_list = baker.make('posts.Like', post=self.post, user=self.user)
        like_lli = baker.make('posts.Like', post=self.post1, user=self.user)
        like_list_user = baker.make('posts.Like', post=self.post, user=self.user1)

        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/likes')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # self.assertEqual(response.data['results'][1]['like_post'], self.post)

    # def test(self):
    #     for _ in range(10):
    #         self.a()
    #         print('---')
    #
    #     self.fail()
    #
    # def a(self):
    #     post = baker.make('posts.Post')
    #     # comments = baker.make('posts.Comment', post=post, _quantity=2, parent=None)
    #     Comment.objects.create(post=post, user=post.user, contents='First')
    #     Comment.objects.create(post=post, user=post.user, contents='Second')
    #
    #     print(post.comments.all())
    #     for comment in post.comments.all():
    #         print(comment.id, comment.contents, comment.created_at, comment.tree_id, comment.lft, comment.parent)
