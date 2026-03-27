import pytest
from app import create_app


@pytest.fixture
def app():
    app = create_app('testing')
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_index(client):
    """Test index page loads"""
    response = client.get('/')
    assert response.status_code == 200
