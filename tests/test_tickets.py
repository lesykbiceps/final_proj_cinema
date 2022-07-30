from app.models import SessionModel, TicketModel, session


def test_free_seats(client, app, authentication_headers):
    lst = []
    for i in range(1, 51):
        lst.append(i)
    resp = client.get(
        '/free_seats/1',
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['Available seats for this session'] == lst


def test_ticket_not_found(client, app, authentication_headers):
    resp = client.get(
        '/tickets/100',
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['message'] == 'Tickets not found.'


def test_sold_tickets_for_new_film(client, app, authentication_headers):
    resp = client.get(
        '/sold_tickets/1',
        headers=authentication_headers(is_admin=True)
    )
    assert resp.json['Sold tickets for this film'] == 0


def test_buy_ticket(client, app, authentication_headers):
    resp = client.post(
        '/tickets',
        json={
            'seat': 75,
            'user_id': 1,
            'session_id': 2
        }, headers=authentication_headers(is_admin=True)
    )
    assert resp.json['seat'] == 75


def test_seat_not_allowed(client, app, authentication_headers):
    resp = client.post(
        '/tickets',
        json={
            'seat': 75,
            'user_id': 1,
            'session_id': 2
        }, headers=authentication_headers(is_admin=True)
    )
    assert resp.json['Please, choose another seat. Places that are not available'] == [75]


def test_no_seats_available(client, app, authentication_headers):
    session_id = 1
    session_ = session.query(SessionModel).filter(SessionModel.id == session_id).first()
    number_seats = session_.number_seats = 0
    sess = SessionModel(number_seats=number_seats)
    sess.save_to_db()
    resp = client.post(
        '/tickets',
        json={
            'seat': 75,
            'user_id': 1,
            'session_id': 2
        }, headers=authentication_headers(is_admin=True)
    )
    assert resp.json['message'] == "Sorry,but there are no more tickets available for this session"
