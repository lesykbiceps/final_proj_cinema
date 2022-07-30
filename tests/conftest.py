import os

import pytest

TEST_USERNAME = "test@example.com"
TEST_PASSWORD = "test@example.com"
ADMIN_TEST_USERNAME = "admintest@example.com"
ADMIN_TEST_PASSWORD = "admintest@example.com"


@pytest.fixture
def app(monkeypatch):
    db_path = os.path.abspath("test.db")
    monkeypatch.setenv('SQLALCHEMY_DATABASE_URI', f"sqlite:///{db_path}")
    from app.main import create_app

    app = create_app()

    return app


@pytest.fixture
def client(app):
    """A test client for the app."""
    app.testing = True
    return app.test_client()


@pytest.fixture
def authentication_headers(client):
    def _authentication_headers(is_admin: bool):
        if is_admin:
            username = ADMIN_TEST_USERNAME
            password = ADMIN_TEST_PASSWORD

        else:
            username = TEST_USERNAME
            password = TEST_PASSWORD

        resp = client.post(
            '/auth/login',
            json={
                "username": username,
                "password": password,
            }
        )

        if resp.json['message'] == f"User {username} doesn't exist":
            resp = client.post(
                '/auth/registration',
                json={
                    "name": username,
                    "age": 18,
                    "username": username,
                    "password": password,
                    "email": "testemail",
                    "is_admin": is_admin
                }
            )

        auth_token = resp.json['access_token']
        headers = {"Authorization": f"Bearer {auth_token}"}

        return headers

    return _authentication_headers
