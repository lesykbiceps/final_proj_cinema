from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required

from app.models import UserModel
from app.decorators import admin_group_required

users_bp = Blueprint('users', __name__)


@users_bp.route("/users", methods=["GET"])
@jwt_required()
@admin_group_required
def get_users():
    """
        Get all users from database. This function does not accept parameters and can be called only by admin
            Returns:
                All users as list of dictionaries.
        """
    users = UserModel.return_all()
    return jsonify(users)


@users_bp.route("/users/<int:id_>", methods=["GET"])
@jwt_required()
@admin_group_required
def get_user(id_):
    """
        Get some specific user from database. This function  accept id_ parameters.
        Only admin can get user
            Args:
                id_: id of user what you want to get
            Returns:
                User with bring id.
        """
    user = UserModel.find_by_id(id_)
    if not user:
        return jsonify({"message": "User not found."}), 404

    return jsonify(user)


@users_bp.route("/users", methods=["POST"])
@jwt_required()
@admin_group_required
def create_user():
    """
        Create  user with some fields. Only admins can create user. Password will store as hashed field.
        Admin should fill in all fields to create a user. Default value for field "is_admin": false
            Example:
                >> {"name":'test',"age": 25, "username":'test_username', "password":'test_pass',
                "email":'test@gmail.com',"is_admin":True}
            Returns:
                "id":2, "name": 'test'
        """
    if not request.json:
        return jsonify({"message": 'Please, specify "username", "name","email", "password" and "age".'}), 400

    age = request.json.get("age")
    name = request.json.get("name")
    username = request.json.get("username")
    password = request.json.get("password")
    email = request.json.get("email")
    is_admin = request.json.get("is_admin", False)
    if not (age and name and username and email and password):
        return jsonify({"message": 'Please, specify "username", "name", "email", "password" and "age".'}), 400

    user = UserModel(
        name=name, age=age, username=username, is_admin=is_admin, email=email,
        hashed_password=UserModel.generate_hash(password))
    user.save_to_db()

    return jsonify({"id": user.id, "name": user.name}), 201


@users_bp.route("/users/<int:id_>", methods=["PATCH"])
@jwt_required()
@admin_group_required
def update_user(id_):
    """
        Update some field in user object or all fields. Only admins can update user.
        If user doesn't exist it will return message: "User not found"
            Example:
                >> {"name":'Bob'}
            Args:
                id_: id of user what you want to update
            Returns:
                "message":"Updated"
        """
    age = request.json.get("age")
    name = request.json.get("name")
    username = request.json.get("username")
    password = request.json.get("password")
    email = request.json.get("email")
    is_admin = request.json.get("is_admin")

    user = UserModel.find_by_id(id_, to_dict=False)
    if not user:
        return jsonify({"message": "User not found."}), 404

    if isinstance(is_admin, bool):
        user.is_admin = is_admin
    if age:
        user.age = age
    if name:
        user.name = name
    if username:
        user.username = username
    if email:
        user.email = email
    if password:
        user.hashed_password = UserModel.generate_hash(password)
    user.save_to_db()
    return jsonify({"message": "Updated"})


@users_bp.route("/users/<int:id_>", methods=["DELETE"])
@jwt_required()
@admin_group_required
def delete_user(id_):
    """
        Delete user object by id. Only admins can delete user.
        If user doesn't exist it will return message: "User not found"
            Args:
                id_: id of user what you want to delete
            Returns:
                "message":"User was successfully deleted"
        """
    code = UserModel.delete_by_id(id_)
    if code == 404:
        return jsonify({"message": "User not found."}), 404

    return jsonify({"message": "Deleted"})
