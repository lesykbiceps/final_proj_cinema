from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required

from app.models import HallModel
from app.decorators import admin_group_required

halls_bp = Blueprint('halls', __name__)


@halls_bp.route("/halls", methods=["GET"])
@jwt_required()
@admin_group_required
def get_halls():
    """
        Get all halls in cinema. Only admins can get halls.
            Returns:
                All halls as list of dictionaries.
        """
    halls = HallModel.return_all()
    return jsonify(halls)


@halls_bp.route("/halls/<int:id_>", methods=["GET"])
@jwt_required()
@admin_group_required
def get_hall(id_):
    """
        Get some specific hall from database. This function  accept id_ parameters.
            Args:
                id_: id of hall what you want to get
            Returns:
                Hall with bring id.
        """
    hall = HallModel.find_by_id(id_)
    if not hall:
        return jsonify({"message": "Hall not found."}), 404

    return jsonify(hall)


@halls_bp.route("/halls", methods=["POST"])
@jwt_required()
@admin_group_required
def create_hall():
    """
        Create  hall with some fields. Only admins can create hall
                Example:
                    >> {"name":'IMAX',"capacity": 75}
                Returns:
                    "id":1, "name": IMAX
        """
    if not request.json:
        return jsonify({"message": 'Please, specify "name" and "capacity".'}), 400

    name = request.json.get("name")
    capacity = request.json.get("capacity")

    if not (capacity and name):
        return jsonify({"message": 'Please, specify "name" and "capacity".'}), 400

    hall = HallModel(
        name=name, capacity=capacity, )

    hall.save_to_db()

    return jsonify({"id": hall.id, "name": hall.name}), 201


@halls_bp.route("/halls/<int:id_>", methods=["PATCH"])
@jwt_required()
@admin_group_required
def update_hall(id_):
    """
        Update some field in hall object or all fields. Only admins can update hall.
        If hall doesn't exist it will return message: "Hall not found"
            Example:
                >> {"name":'CINEMATIX'}
            Args:
                id_: id of hall what you want to update
            Returns:
                "message":"Updated"
        """
    name = request.json.get("name")
    capacity = request.json.get("capacity")

    hall = HallModel.find_by_id(id_, to_dict=False)
    if not hall:
        return jsonify({"message": "Hall not found."}), 404

    if name:
        hall.name = name
    if capacity:
        hall.capacity = capacity
    hall.save_to_db()
    return jsonify({"message": "Updated"})


@halls_bp.route("/halls/<int:id_>", methods=["DELETE"])
@jwt_required()
@admin_group_required
def delete_hall(id_):
    """
        Delete hall object by id. Only admins can delete hall.
        If hall doesn't exist it will return message: "Hall not found"
            Args:
                id_: id of hall what you want to delete
            Returns:
                "message":"Hall was successfully deleted"
        """
    code = HallModel.delete_by_id(id_)
    if code == 404:
        return jsonify({"message": "Hall not found."}), 404

    return jsonify({"message": "Hall was successfully deleted"})
