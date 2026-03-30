import pytest
from datetime import date
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from user.models import *

User = get_user_model()

@pytest.fixture
def user() -> User:
    return User.objects.create_user(username="testuser",password="testpassword")


@pytest.fixture()
def api_client() -> APIClient:
    yield APIClient()

    