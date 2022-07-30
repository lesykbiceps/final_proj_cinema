def test_register(client, app):
    assert client.post(
        '/auth/registration',
        json={
            "name": "Test",
            "age": 23,
            "username": " test",
            "password": "test123pass",
            "email": "test1email",
            "is_admin": True,
        }
    ).json["message"] == 'User  test was created'


def test_user_already_exists(client, app):
    assert client.post(
        '/auth/registration',
        json={
            "name": "Test",
            "age": 23,
            "username": " test",
            "password": "test123pass",
            "email": "test1email",
            "is_admin": True
        }
    ).json["message"] == "User  test already exists"


def test_register_fail_exception(client, app):
    assert client.post(
        '/auth/registration',
        json={
            "name": "Mark",
            "age": 23,
            "username": " mark",
            "password": "markpass",
            "email": "markemail",
            "is_admin": "True"
        }
    ).json["message"] == "Something went wrong while creating"


def test_login_fail(client, app):
    assert client.post(
        '/auth/login',
        json={
            "password": 23,
        }
    ).json["message"] == 'Please, provide "username" and "password" in body.'


def test_login_wrong_password(client, app):
    assert client.post(
        '/auth/login',
        json={
            "username": " john",
            "password": "23",
        }
    ).json["message"] == 'Wrong password'
