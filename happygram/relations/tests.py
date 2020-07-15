from model_bakery import baker
from munch import Munch
from rest_framework import status
from rest_framework.test import APITestCase


class UserRelationTestCase(APITestCase):
    def setUp(self) -> None:
        self.users = baker.make('users.User', _quantity=2)
        self.data = {
            'to_user': self.users[1].id,
            'related_type': 'f',
        }

    def test_user_follow(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post('/api/relations', data=self.data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        follow_response = Munch(response.data)
        self.assertEqual(follow_response.to_user, self.data['to_user'])
        self.assertEqual(follow_response.related_type, self.data['related_type'])
        self.assertEqual(follow_response.from_user, self.users[0].id)

