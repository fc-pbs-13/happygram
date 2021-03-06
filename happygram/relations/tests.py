from model_bakery import baker
from munch import Munch
from redlock import Redlock
from rest_framework import status
from rest_framework.test import APITestCase
from profiles.models import Profile
from model_bakery import baker
from relations.models import Relation

users = baker.make('users.User', _quantity=2)
Relation.objects.create(from_user=users[0], to_user=users[1], related_type='FOLLOW')


class UserRelationTestCase(APITestCase):
    def setUp(self) -> None:
        self.users = baker.make('users.User', _quantity=2)
        self.data = {
            'to_user': self.users[1].id,
            'related_type': Relation.RelationChoice.FOLLOW
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
        self.relation = Relation.objects.create(from_user=self.users[0], to_user=self.users[1],
                                                related_type=Relation.RelationChoice.FOLLOW)

        self.client.force_authenticate(user=self.users[0])

        response = self.client.delete(f'/api/relations/{self.relation.id}')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Relation.objects.filter(pk=self.relation.id).exists())

    def test_relations_update(self):
        relation = Relation.objects.create(from_user=self.users[0], to_user=self.users[1],
                                           related_type=Relation.RelationChoice.FOLLOW)
        update_data = {
            'related_type': Relation.RelationChoice.BLOCK,
            'to_user': relation.to_user.id
        }
        self.client.force_authenticate(user=self.users[0])

        response = self.client.patch(f'/api/relations/{relation.id}', data=update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        follow_response = Munch(response.data)
        self.assertEqual(follow_response.related_type, update_data['related_type'])

    def test_relations_duplicate(self):
        Relation.objects.create(from_user=self.users[0], to_user=self.users[1],
                                related_type=Relation.RelationChoice.BLOCK)

        self.client.force_authenticate(user=self.users[0])

        response = self.client.post('/api/relations', data=self.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_following_count_increase(self):
        self.client.force_authenticate(user=self.users[0])

        self.client.post('/api/relations', data=self.data)

        qs = Profile.objects.all()
        self.assertEqual(qs.get(user=self.users[0]).following, 1)
        self.assertEqual(qs.get(user=self.users[1]).follower, 1)

    def test_following_count_decrease(self):
        self.client.force_authenticate(user=self.users[0])
        relation = baker.make('relations.Relation', from_user=self.users[0], to_user=self.users[1],
                              related_type=Relation.RelationChoice.FOLLOW)
        self.users[0].profile.following = 10
        self.users[0].profile.save()

        self.client.delete(f'/api/relations/{relation.id}')

        qs = Profile.objects.all()
        self.assertEqual(qs.get(user=self.users[0]).following, 9)


class TestRedlock(APITestCase):

    def setUp(self):
        self.redlock = Redlock([{"host": "localhost"}])

    def test_lock(self):
        lock = self.redlock.lock("pants", 100)
        print(lock)
        self.assertEqual(lock.resource, "pants")
        self.redlock.unlock(lock)

        lock = self.redlock.lock("pants", 10)
        print(lock)
        self.redlock.unlock(lock)
