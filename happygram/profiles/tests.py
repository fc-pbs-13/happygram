from model_bakery import baker
from munch import Munch
from rest_framework import status
from rest_framework.test import APITestCase

from profiles.models import Profile


class ProfileTestCase(APITestCase):
    def setUp(self) -> None:
        self.users = baker.make('users.User', _quantity=3)
        self.profiles = []

        for user in self.users:
            self.profiles += baker.make('profiles.Profile', _quantity=3, introduce='hi django', user=user)

        self.user = self.users[0]
        self.profile = Profile.objects.filter(user=self.user.id).first()

    def test_profile_detail(self):
        """"프로필 디테일"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/profiles/{self.profile.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile_response = Munch(response.data)

        self.assertTrue(profile_response.id)
        self.assertEqual(profile_response.user, self.user.id)
        self.assertEqual(profile_response.introduce, self.profile.introduce)

    def test_profile_update(self):
        """프로필 업데이트"""
        prev_introduce = self.profile.introduce
        data = {
            'introduce': 'hi python'
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(f'/api/profiles/{self.profile.id}', data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile_response = Munch(response.data)
        self.assertEqual(profile_response.introduce, data['introduce'])
        self.assertNotEqual(profile_response.introduce, prev_introduce)

