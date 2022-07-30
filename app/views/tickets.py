from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt

from app.models import TicketModel, SessionModel, UserModel, session
from app.decorators import admin_group_required

tickets_bp = Blueprint('tickets', __name__)


@tickets_bp.route("/tickets", methods=["GET"])
@jwt_required()
@admin_group_required
def get_tickets():
    """
        Get all tickets from database. This function does not accept parameters
            Returns:
                All tickets as list of dictionaries.
    """
    tickets = TicketModel.return_all()
    return jsonify(tickets)


@tickets_bp.route("/mytickets", methods=["GET"])
@jwt_required()
def get_my_tickets():
    """
        User can view the history of ticket purchases. This function does not accept parameters
                Returns:
                    All user's tickets as list of dictionaries.
        """
    jwt = get_jwt()
    name = jwt.get("sub")
    user = session.query(UserModel).filter(UserModel.name == name).first()
    id_ = user.id
    tickets = TicketModel.find_by_user_id(id_, 0, 10)
    return jsonify(tickets)


@tickets_bp.route("/free_seats/<int:id_>", methods=["GET"])
@jwt_required()
def get_free_seats_by_session(id_):
    """
        User can see which places are available for a particular session.This function accept parameter: session id
                    Returns:
                        All available places for session.
            """
    blocked = session.query(TicketModel).filter(TicketModel.session_id == id_).all()
    lst = []
    lst_seats = []
    lst_sessions = []
    for s in blocked:
        lst.append(s.seat)
    session_ = session.query(SessionModel).filter(SessionModel.id == id_).first()
    session__ = SessionModel.return_all()

    for s in session__:
        lst_sessions.append(s['id'])

    if id_ not in lst_sessions:
        return jsonify({"message": "Such session not exist. Please,try another one"}), 400

    count_seats = len(lst) + session_.number_seats
    for i in range(1, count_seats + 1):
        if i not in lst:
            lst_seats.append(i)
    result = lst_seats
    return jsonify({"Available seats for this session": result})


@tickets_bp.route("/tickets/<int:id_>", methods=["GET"])
@jwt_required()
@admin_group_required
def get_tickets_by_session_id(id_):
    """
        Admin can get some tickets for specific session from database.
        This function  accept id_ parameters - session_id.
            Args:
                id_: id of session what you want to get
            Returns:
                Tickets with bring session_id.
        """
    tickets = TicketModel.find_by_session_id(id_, 0, 75)
    if not tickets:
        return jsonify({"message": "Tickets not found."}), 404

    return jsonify(tickets)


@tickets_bp.route("/sold_tickets/<int:id_>", methods=["GET"])
@jwt_required()
@admin_group_required
def get_tickets_by_film_id(id_):
    """
        Admin can view a statistic of sold tickets for selected film.
        He can check how many tickets were sold for a particular movie
        Args:
                id_: id of film about which you want to get statistic
            Returns:
                Number of tickets that were sold for a particular movie
    """
    sessions = SessionModel.find_by_film_id(id_, 0, 120)
    lst = []
    for elem in sessions:
        blocked = session.query(TicketModel).filter(TicketModel.session_id == elem["id"]).all()
        for s in blocked:
            lst.append(s.seat)
    result = len(lst)
    return jsonify({"Sold tickets for this film": result})


@tickets_bp.route("/tickets", methods=["POST"])
@jwt_required()
def create_ticket():
    """
        The main method of this program is responsible for buying a ticket.
        If there are no more seats for the session or selected seat is not available, you will be notified.
        Using the method above, you can see which seats are available and buy a ticket.
            Example:
                >> {"seat":50,"user_id":1, "session_id":1}
            Returns:
                "id":1, "seat": 50
        """
    if not request.json:
        return jsonify({"message": 'Please, specify "seat", "user_id" and "session_id".'}), 400
    seat = request.json.get("seat")
    user_id = request.json.get("user_id")
    session_id = request.json.get("session_id")
    blocked = session.query(TicketModel).filter(TicketModel.session_id == session_id).all()
    lst = []
    for s in blocked:
        lst.append(s.seat)
    if not (seat and user_id and session_id):
        return jsonify({"message": 'Please, specify "seat", "user_id" and "session_id".'}), 400

    if seat in lst:
        return jsonify({'Please, choose another seat. Places that are not available': lst})

    session_ = session.query(SessionModel).filter(SessionModel.id == session_id).first()

    if session_.number_seats > 0:
        ticket = TicketModel(
            seat=seat, user_id=user_id, session_id=session_id)
        ticket.save_to_db()
        session_.number_seats -= 1
        session_.save_to_db()
        return jsonify({"id": ticket.id, "seat": ticket.seat}), 201

    if session_.number_seats <= 0:
        return jsonify({"message": "Sorry,but there are no more tickets available for this session"})
