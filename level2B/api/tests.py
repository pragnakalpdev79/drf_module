from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory,APIClient
from rest_framework_simplejwt.tokens import AccessToken

class ExceptionHandlerTest(APITestCase):

    def setUp(self):
        # self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # self.client = APIClient()
        # token = AccessToken.for_user(user=self.user)
        # self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    def test_permission_denied(self):
        self.client.force_authenticate(user=self.user)

    def test_authentication_error(self): #testing for requests without token!
        response = self.client.post('/api/tasks/')
        self.assertEqual(response.status_code,401)
        self.assertIn('error',response.data)
        self.assertEqual(response.data['error']['details']['code'],'authentication_required')


    def test_validation_error(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/tasks/',{
            'title': '',
            "completed" : False
        })
        self.assertEqual(response.status_code,400)
        self.assertIn('error',response.data)
        self.assertIn('fields',response.data['error']['details'])
        self.assertIn('title',response.data['error']['details']['fields'])



