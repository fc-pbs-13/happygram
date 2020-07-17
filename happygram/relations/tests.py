from model_bakery import baker
from munch import Munch
from rest_framework import status
from rest_framework.test import APITestCase
from relations.models import Relation


class UserRelationTestCase(APITestCase):
    def setUp(self) -> None:
        self.users = baker.make('users.User', _quantity=2)
        self.data = {
            'to_user': self.users[1].id,
            'related_type': 'f'
        }

    def test_relations_create(self):
        self.client.force_authenticate(user=self.users[0])

        response = self.client.post('/api/relations', data=self.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        follow_response = Munch(response.data)
        self.assertEqual(follow_response.to_user, self.data['to_user'])
        self.assertEqual(follow_response.related_type, self.data['related_type'])
        self.assertEqual(follow_response.from_user, self.users[0].id)

    def test_relations_destroy(self):
        relation = Relation.objects.create(from_user=self.users[0], to_user=self.users[1], related_type='f')

        response = self.client.delete(f'/api/relations/{relation.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Relation.objects.filter(pk=relation.id).exists())

    def test_relations_update(self):
        relation = Relation.objects.create(from_user=self.users[0], to_user=self.users[1], related_type='follow')
        update_data = {
            'related_type': 'block',
            'to_user': relation.to_user.id
        }
        response = self.client.patch(f'/api/relations/{relation.id}', data=update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        follow_response = Munch(response.data)
        self.assertEqual(follow_response.related_type, update_data['related_type'])

    def test_relations_duplicate(self):
        Relation.objects.create(from_user=self.users[0], to_user=self.users[1], related_type='b')

        self.client.force_authenticate(user=self.users[0])

        response = self.client.post(f'/api/relations', data=self.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)


