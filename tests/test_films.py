def test_get_film_info_fail_not_exist(client, app, authentication_headers):
    resp = client.get(
        '/films/100',
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['message'] == 'Film not found.'


def test_get_films_if_not_exist(client, app, authentication_headers):
    resp = client.get(
        '/films',
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json == []


def test_get_film_info(client, app, authentication_headers):
    resp = client.get(
        '/films/2',
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['id'] == 2


def test_create_film(client, app, authentication_headers):
    resp = client.post(
        '/films',
        json={
            'name': 'test',
            'genre': 'test',
            'director': 'test',
            'rating': 5,
            'image': "test"
        }, headers=authentication_headers(is_admin=True)
    )
    assert resp.json['name'] == 'test'


def test_update_film(client, app, authentication_headers):
    resp = client.patch(
        '/films/1',
        json={
            "name": "Uncharted"
        },
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['message'] == "Updated"


def test_create_film_fail(client, app, authentication_headers):
    resp = client.post(
        '/films',
        json={
            "name": "Spiderman"
        },
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['message'] == 'Please, specify "name", "genre", "director", "image" and "rating".'