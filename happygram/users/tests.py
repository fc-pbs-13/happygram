from model_bakery import baker

from profiles.models import Profile
from relations.models import Relation
from users.models import User
from django.test import TestCase
from munch import Munch
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class UserTestCase(APITestCase):
    def setUp(self) -> None:
        self.password = "1111"
        self.data = {"email": "test@test.com", "password": self.password}
        self.test_user = User.objects.create(**self.data)
        self.test_user.set_password(raw_password=self.password)
        self.test_user.save()

    def test_should_detail_user(self):
        """
        User detail
        Request : GET - /api/user/{user_id}
        """
        self.client.force_authenticate(user=self.test_user)
        response = self.client.get(f'/api/users/{self.test_user.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_response = Munch(response.data)
        self.assertEqual(user_response.id, self.test_user.id)
        self.assertEqual(user_response.email, self.test_user.email)

    def test_should_create_user(self):
        """
        Request : POST - /api/user/
        """
        data = {"email": "new@new.com", "password": self.password}
        response = self.client.post('/api/users', data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user_response = Munch(response.data)
        #  create profile object
        self.assertTrue(Profile.objects.filter(user_id=user_response.id))
        self.assertTrue(user_response.id)
        self.assertEqual(user_response.email, data['email'])

    def test_should_delete_user(self):
        """
        Request : DELETE - /api/user/{user_id}
        """
        self.client.force_authenticate(user=self.test_user)
        response = self.client.delete(f'/api/users/{self.test_user.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.test_user.id).exists())

    def test_should_update_password(self):
        """
        Request : PATCH - /api/user/{user_id}
        """
        prev_email = self.test_user.email
        self.client.force_authenticate(user=self.test_user)
        data = {"email": "changed@gmail.com"}

        response = self.client.patch(f'/api/users/{self.test_user.id}', data=data)

        user_response = Munch(response.data)
        self.assertNotEqual(user_response.email, prev_email)

    def test_should_login(self):
        """
        Request : POST - /api/user/login
        """
        response = self.client.post('/api/users/login', data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user_response = Munch(response.data)
        self.assertTrue(user_response.token)
        self.assertTrue(Token.objects.filter(key=user_response.token).exists())

    def test_should_login_fail(self):
        """
        Request : POST - /api/user/login
        """
        self.fail_data = {"email": "test@test.com", "password": self.password + "0"}

        response = self.client.post('/api/users/login', data=self.fail_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertFalse('token' in response.data)

    def test_should_logout(self):
        """
        Request : DELETE - /api/user/logout
        """
        response = self.client.post('/api/users/login', data=self.data)
        token = response.data['token']

        self.client.force_authenticate(user=self.test_user, token=token)
        response = self.client.delete('/api/users/logout')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(pk=token).exists())

    def test_update_password(self):
        update_pwd = {"password": "2222"}

        token = Token.objects.create(user=self.test_user)
        self.client.force_authenticate(user=self.test_user, token=token.key)

        response = self.client.patch('/api/users/update_password', data=update_pwd)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        update_login = {"email": "test@test.com", "password": update_pwd['password']}
        response2 = self.client.post('/api/users/login', data=update_login)
        self.assertTrue(response2.data['token'])


class UserFollowTestCase(APITestCase):
    def setUp(self) -> None:
        self.users = baker.make('users.User', _quantity=3)
        self.user_data = {'user': self.users[0]}
        Relation.objects.create(from_user=self.users[0], to_user=self.users[1],
                                related_type=Relation.RelationChoice.FOLLOW)
        Relation.objects.create(from_user=self.users[0], to_user=self.users[2],
                                related_type=Relation.RelationChoice.FOLLOW)
        Relation.objects.create(from_user=self.users[1], to_user=self.users[0],
                                related_type=Relation.RelationChoice.FOLLOW)

    def test_follower_list(self):
        response = self.client.get(f"/api/users/{self.user_data['user'].id}/follow")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for response_data in response.data['results']:
            r = Munch(response_data)
            # response 에 from_user와 profile - user가 Relation objects에 있어야 한다
            self.assertTrue(Relation.objects.filter(from_user=r.from_user, to_user=r.profile['user'],
                                                    related_type=Relation.RelationChoice.FOLLOW))

    def test_following_list(self):
        response = self.client.get(f"/api/users/{self.user_data['user'].id}/following")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for response_data in response.data['results']:
            r = Munch(response_data)
            # response 에  to_user와 profile-user가 Relation objects에 있어야 한다
            self.assertTrue(Relation.objects.filter(from_user=r.to_user, to_user=r.profile['user'],
                                                    related_type=Relation.RelationChoice.FOLLOW))


class UserBlockTestCase(APITestCase):
    def setUp(self) -> None:
        self.users = baker.make('users.User', _quantity=3)
        self.user_data = {'user': self.users[0]}

        Relation.objects.create(from_user=self.users[0], to_user=self.users[1],
                                related_type=Relation.RelationChoice.BLOCK)
        Relation.objects.create(from_user=self.users[0], to_user=self.users[2],
                                related_type=Relation.RelationChoice.BLOCK)
        Relation.objects.create(from_user=self.users[2], to_user=self.users[0],
                                related_type=Relation.RelationChoice.BLOCK)

    def test_block_list(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(f"/api/users/block")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for response_data in response.data['results']:
            r = Munch(response_data)
            self.assertTrue(Relation.objects.filter(from_user=r.from_user, to_user=r.profile['user'],
                                                    related_type=Relation.RelationChoice.BLOCK))
