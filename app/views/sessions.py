import math
from datetime import datetime

from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required

from app.models import SessionModel, HallModel, FilmModel, session
from app.decorators import admin_group_required


sessions_bp = Blueprint('sessions', __name__)


@sessions_bp.route("/sessions", methods=["GET"])
@jwt_required()
def get_sessions():
    """
        Get all sessions with some filter of film fields or without it. You can filter by: film genre,name,actor,
        director, started time of session. Also, you can sort sessions by date.
            Example 1:
                >> /sessions?genre=superhero
            Returns:
                Session(s) where film genre is superhero
            Example 2:
                >> /sessions?sort=True
            Returns:
                Session(s) sorted by datetime
        """
    genre = request.args.get('genre')
    name = request.args.get('film_name')
    actor_name = request.args.get('actor_name')
    director = request.args.get('director')
    started_at = request.args.get('started_at')
    sorted_sessions = request.args.get('sort')
    result = SessionModel.return_all()
    if genre:
        result = SessionModel.find_by_genre(genre)
    if name:
        result = SessionModel.find_by_name(name)
    if actor_name:
        result = SessionModel.find_by_actor(actor_name)
    if director:
        result = SessionModel.find_by_director(director)
    if started_at:
        started_time = datetime.strptime(started_at, '%Y-%m-%d %H:%M:%S')
        result = SessionModel.find_by_date(started_time)
    if sorted_sessions == 'True' or sorted_sessions == '1':
        sessions = SessionModel.return_all()
        result = sorted(
            sessions,
            key=lambda x: (x['started_at']), reverse=False
        )
    return jsonify(result)


@sessions_bp.route("/sessions", methods=["POST"])
@jwt_required()
@admin_group_required
def create_session():
    """
        Create  session with some fields. Only admins can create session.
        If timeline in hall is already reserved by another session then you will get message with info about it
            Example:
                >> {"film_id":1, "hall_id":1, "started_at":'2022-06-01 10:00:00', "number_seats":50}
            Returns:
                "id":1, "started_at": '2022-06-01 10:00:00'
        """
    if not request.json:
        return jsonify({"message": 'Please, specify "film_id", "hall_id", "number_seats" and "started_at".'}), 400

    film_id = request.json.get("film_id")
    hall_id = request.json.get("hall_id")
    started_at = request.json.get("started_at")
    started_at = datetime.strptime(started_at, '%Y-%m-%d %H:%M:%S')
    number_seats = session.query(HallModel.capacity).filter(HallModel.id == hall_id)

    sessions = SessionModel.return_all()
    for elem in sessions:
        if hall_id == elem['hall_id']:
            difference = started_at - elem['started_at']
            difference = difference.total_seconds() / 60
            difference = math.fabs(difference)
            if difference < 120:
                return jsonify({"message": 'At this time, another film has already been registered in the hall.'
                                           ' Please choose another time'})

    if not (film_id and hall_id and started_at and number_seats):
        return jsonify({"message": 'Please, specify "film_id", "hall_id", "number_seats" and "started_at".'}), 400

    lst_halls = []
    lst_films = []
    halls = HallModel.return_all()
    films = FilmModel.return_all()
    for h in halls:
        lst_halls.append(h['id'])
    for f in films:
        lst_films.append(f['id'])

    if hall_id not in lst_halls:
        return jsonify({"message": 'Such hall not exist. Please, choose another one.'}), 400
    if film_id not in lst_films:
        return jsonify({"message": 'Such film not exist. Please, choose another one.'}), 400

    sess = SessionModel(
        film_id=film_id, hall_id=hall_id, started_at=started_at, number_seats=number_seats)
    sess.save_to_db()

    return jsonify({"id": sess.id, "started_at": sess.started_at, "film_id": sess.film_id}), 201


@sessions_bp.route("/sessions/<int:id_>", methods=["DELETE"])
@jwt_required()
@admin_group_required
def delete_session(id_):
    """
        Delete session object by id. Only admins can delete film.
        If session doesn't exist it will return message: "Session not found"
            Args:
                id_: id of session what you want to delete
            Returns:
                "message":"Session was successfully deleted"
                    """
    code = SessionModel.delete_by_id(id_)
    if code == 404:
        return jsonify({"message": "Session not found."}), 404

    return jsonify({"message": "Session was successfully deleted"})
