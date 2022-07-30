from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required

from app.models import ActorModel
from app.decorators import admin_group_required

actors_bp = Blueprint('actors', __name__)


@actors_bp.route("/actors", methods=["GET"])
@jwt_required()
@admin_group_required
def get_actors():
    """
        Get all actors from database. This function does not accept parameters
            Returns:
                All actors as list of dictionaries.
    """
    film_id = request.args.get('film_id')
    result = ActorModel.return_all()
    if film_id:
        result = ActorModel.find_by_film_id(film_id, 0, 20)
    return jsonify(result)


@actors_bp.route("/actors", methods=["POST"])
@jwt_required()
@admin_group_required
def create_actors():
    """
        Create  actor with some fields. Only admins can add actor
            Example:
                >> {"name":'Future',"genre":'superhero', "director":'Bob Ace', "rating":8.9}
            Returns:
                "id":1, "name": Future
        """
    if not request.json:
        return jsonify({"message": 'Please, specify "name" and "surname".'}), 400

    name = request.json.get("name")
    surname = request.json.get("surname")
    if not (surname and name):
        return jsonify({"message": 'Please, specify "name" and "surname".'}), 400

    actor = ActorModel(
        name=name, surname=surname)

    actor.save_to_db()

    return jsonify({"id": actor.id, "name": actor.name}), 201


@actors_bp.route("/actors/<int:id_>", methods=["DELETE"])
@jwt_required()
@admin_group_required
def delete_actor(id_):
    """
        Delete actor object by id. Only admins can delete actor.
        If actor doesn't exist in database it will return message: "Actor not found"
            Args:
                id_: id of actor what you want to delete
            Returns:
                "message":"Actor was successfully deleted"
                    """
    code = ActorModel.delete_by_id(id_)
    if code == 404:
        return jsonify({"message": "Actor not found."}), 404

    return jsonify({"message": "Actor was successfully deleted"})
