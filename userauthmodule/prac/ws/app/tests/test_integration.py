import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Task

class TaskIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_task_workflow(self):
        response = self.client.post('/api/tasks/',
                                    {
                                        'title' : 'Test Task',
                                        'desc' : 'Description',
                                    })
        self.assertEqual(response.status_code,201)
        task_id = response.data['id']
        response = self.client.patch(f'/api/tasks/{task_id}/',{
            'completed': True
        })
        self.assertEqual(response.status_code,200)

        response = self.client.delete(f'/api/tasks/{task_id}/')
        self.assertEqual(response.status_code,204)