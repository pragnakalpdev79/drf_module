import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import Task

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser',password='testpass123')

# @pytest.fixture
# def task(user):
#     return User.objects.create(title='Test Task',owner=user)

@pytest.mark.django_db
def test_create_task(api_client,user):
    api_client.force_authenticate(user=user)
    response = api_client.post('/api/v1/task/',{
        'title': 'New Task',
        'desc': 'Description',
        'completed' : False,
        'priority' : 'm',
    })
    assert response.status_code == 201
    assert Task.objects.count() == 1

@pytest.mark.django_db
def test_list_tasks(api_client,user):
    print(user)
    api_client.force_authenticate(user=user)
    print("ac",api_client)
    response = api_client.get('/api/v1/task/')
    assert response.status_code == 200
    print("response data:- ")
    print(response.renderer_context)
    assert len(response.data) == 1