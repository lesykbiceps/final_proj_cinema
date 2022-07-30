import pytest


def test_get_user_info(client, app, authentication_headers):
    resp = client.get(
        '/users/2',
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['id'] == 2


def test_get_user_info_fail(client, app, authentication_headers):
    resp = client.get(
        '/users/100',
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['message'] == "User not found."


def test_create_user(client, app, authentication_headers):
    resp = client.post(
        '/users',
        json={
            "name": "Bob",
            "age": 26,
            "username": "bob123",
            "password": "bobpass",
            "email": "bobemail",
            "is_admin": False
        },
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['name'] == "Bob"


def test_create_user_fail(client, app, authentication_headers):
    resp = client.post(
        '/users',

        json={
            "name": "Bob",
            "age": 26,
            "username": "bob123",
            "password": "bobpass",
            "is_admin": False
        },
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['message'] == 'Please, specify "username", "name", "email", "password" and "age".'


def test_delete_user(client, app, authentication_headers):
    resp = client.delete(
        '/users/2',
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['message'] == "Deleted"


def test_delete_user_fail(client, app, authentication_headers):
    resp = client.delete(
        '/users/100',
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['message'] == "User not found."


def test_update_user(client, app, authentication_headers):
    resp = client.patch(
        '/users/3',
        json={
            "name": "Jack",
            "age": 99,
            "username": " jack"
        },
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['message'] == "Updated"


@pytest.mark.parametrize(
    "current_str, expected_str",
    [
        ("/users/100", "User not found."),
        ("/users/1000", "User not found."),
        ("/users/10000", "User not found."),
    ]
)
def test_update_user_fail(client, app, authentication_headers, current_str, expected_str):
    resp = client.patch(
        (current_str),
        json={
            "name": "Jack",
            "age": 99,
            "username": " jack"
        },
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['message'] == expected_str
