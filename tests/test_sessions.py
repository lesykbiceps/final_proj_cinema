def test_get_films_if_not_exist(client, app, authentication_headers):
    resp = client.get(
        '/sessions',
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json == []


def test_create_session(client, app, authentication_headers):
    resp = client.post(
        '/sessions',
        json={
            'number_seats': 50,
            'film_id': 1,
            'hall_id': 1,
            'started_at': "2022-06-27 14:00:00"
        }, headers=authentication_headers(is_admin=True)
    )
    assert resp.json['film_id'] == 1


def test_create_session_failed_time(client, app, authentication_headers):
    resp = client.post(
        '/sessions',
        json={
            'number_seats': 50,
            'film_id': 1,
            'hall_id': 1,
            'started_at': "2022-06-27 14:00:00"
        }, headers=authentication_headers(is_admin=True)
    )
    assert resp.json['message'] == 'At this time, another film has already been registered in the hall.' \
                                   ' Please choose another time'


def test_session_filter_empty_list(client, app, authentication_headers):
    resp = client.get(
        '/sessions?film_name=NotEXIST',
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json == []


def test_session_filter_film_name(client, app, authentication_headers):
    resp = client.get(
        '/sessions?film_name=Uncharted',
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json[0]['film_id'] == 1
