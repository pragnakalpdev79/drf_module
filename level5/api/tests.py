import pytest
from rest_framework.test import APITestCase
from rest_framework import status,APIClient
from django.contrib.auth.models import User
from .models import Task

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

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser',password='testpass123')

@pytest.fixture
def task(user):
    return Task.objects.create(title='Test Task',owner=user)

@pytest.mark.django_db
def test_create_task(api_client,user):
    api_client.force_authenticate(user=user)
    response = api_client.post('/api/tasks/',
                               {
                                   'title': 'New Task',
                                   'desc' : 'Description',
                                   'completed' : False
                               })
    assert response.status_code == 201
    assert Task.objects.count == 1

@pytest.mark.django_db
def test_list_tasks(api_client,user,task):
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/tasks/')
    assert response.status_code == 200
    assert len(response.data) == 1