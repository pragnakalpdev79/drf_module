from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class ExceptionHandlerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user1@gmail.com',
            password='testpass123'
        )
    def test_authentication_error(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code,401)
        self.assertIn('error',response.data)
        self.assertEqual(response.data['error']['details']['code'],'authentication_required')
    def test_validation_error(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/post/',{
            'title': '',
            "completed" : False
        })
        self.assertEqual(response.status_code,400)
        self.assertIn('errors',response.data)
        self.assertIn('fields',response.data['error']['details'])
        self.assertIn('title',response.data['error']['details']['fields'])
    def test_permission_denied(self):
        self.client.force_authenticate(user=self.user)
