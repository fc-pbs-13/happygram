from model_bakery import baker
from munch import Munch
from rest_framework import status
from rest_framework.test import APITestCase
from profiles.models import Profile
from users.models import User


class ProfileTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(email="abc@test.com")
        # user create -> profile create
        self.profile = Profile.objects.get(user_id=self.user.id)

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
        """프로필 이미지도 업데이트"""
        prev_introduce = self.profile.introduce
        data = {
            'introduce': 'hi python',
            'image': self.temporary_image()
        }
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(f'/api/profiles/{self.profile.id}', data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        profile_response = Munch(response.data)
        self.assertEqual(profile_response.introduce, data['introduce'])
        self.assertNotEqual(profile_response.introduce, prev_introduce)
