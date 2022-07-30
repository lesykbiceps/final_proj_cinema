from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required

from app.models import FilmModel
from app.decorators import admin_group_required

films_bp = Blueprint('films', __name__)


@films_bp.route("/films", methods=["GET"])
@jwt_required()
def get_films():
    """
        Get all films from database. This function does not accept parameters
            Returns:
                All films as list of dictionaries.
    """
    films = FilmModel.return_all()
    return jsonify(films)


@films_bp.route("/films/<int:id_>", methods=["GET"])
@jwt_required()
def get_film(id_):
    """
        Get some specific film from database. This function  accept id_ parameters.
            Args:
                id_: id of film what you want to get
            Returns:
                Film with bring id.
        """
    film = FilmModel.find_by_id(id_)
    if not film:
        return jsonify({"message": "Film not found."}), 404

    return jsonify(film)


@films_bp.route("/films", methods=["POST"])
@jwt_required()
@admin_group_required
def create_film():
    """
        Create  film with some fields. Only admins can create film
            Example:
                >> {"name":'Future',"genre":'superhero', "director":'Bob Ace',
                 "image":"https://planetakino.ua/res/get-poster/00000000000000000000000000003493/vend.jpg",
                 "rating":8.9}
            Returns:
                "id":1, "name": Future
        """
    if not request.json:
        return jsonify({"message": 'Please, specify "name", "genre", "image", "director" and "rating".'}), 400

    name = request.json.get("name")
    genre = request.json.get("genre")
    director = request.json.get("director")
    rating = request.json.get("rating")
    image = request.json.get("image")
    if not (genre and name and director and rating and image):
        return jsonify({"message": 'Please, specify "name", "genre", "director", "image" and "rating".'}), 400

    film = FilmModel(
        name=name, genre=genre, director=director, rating=rating, image=image)

    film.save_to_db()

    return jsonify({"id": film.id, "name": film.name}), 201


@films_bp.route("/films/<int:id_>", methods=["PATCH"])
@jwt_required()
@admin_group_required
def update_film(id_):
    """
        Update some field in film object or all fields. Only admins can update film.
        If film doesn't exist it will return message: "Film not found"
            Example:
                >> {"name":'Spiderman'}
            Args:
                id_: id of film what you want to update
            Returns:
                "message":"Updated"
                """
    name = request.json.get("name")
    genre = request.json.get("genre")
    director = request.json.get("director")
    rating = request.json.get("rating")
    image = request.json.get("image")

    film = FilmModel.find_by_id(id_, to_dict=False)
    if not film:
        return jsonify({"message": "Film not found."}), 404

    if name:
        film.name = name
    if genre:
        film.genre = genre
    if director:
        film.director = director
    if rating:
        film.rating = rating
    if image:
        film.image = image
    film.save_to_db()
    return jsonify({"message": "Updated"})


@films_bp.route("/films/<int:id_>", methods=["DELETE"])
@jwt_required()
@admin_group_required
def delete_film(id_):
    """
        Delete film object by id. Only admins can delete film.
        If film doesn't exist it will return message: "Film not found"
            Args:
                id_: id of film what you want to delete
            Returns:
                "message":"Film was successfully deleted"
                    """
    code = FilmModel.delete_by_id(id_)
    if code == 404:
        return jsonify({"message": "Film not found."}), 404

    return jsonify({"message": "Film was successfully deleted"})
