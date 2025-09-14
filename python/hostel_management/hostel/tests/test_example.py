import pytest
from django.urls import reverse
from django.test import Client

@pytest.mark.django_db
def test_example():
    client = Client()  # Initialize the test client
    url = reverse('home')  # Replace 'home' with the actual name of your view
    response = client.get(url)
    assert response.status_code == 200