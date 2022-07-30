from flask import jsonify, request, Blueprint
from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt,
    jwt_required, get_jwt_identity, get_current_user, current_user)

from app.models import UserModel, RevokedTokenModel

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/auth/registration", methods=["POST"])
def register():
    """Method for adding a new user (registration).
       Returns access and refresh tokens.
    """
    if not (request.json and request.json.get("username") and request.json.get("password")
            and request.json.get("age") and request.json.get("name") and request.json.get("email")):
        return jsonify({"message": 'Please, provide "age", "name", "email", "username" and "password" in body.'}), 400

    name = request.json["name"]
    age = request.json["age"]
    username = request.json["username"]
    password = request.json["password"]
    email = request.json["email"]
    is_admin = request.json.get("is_admin", False)

    if UserModel.find_by_username(username, to_dict=False):
        return {"message": "User {} already exists".format(username)}, 400

    if UserModel.find_by_email(email, to_dict=False):
        return {"message": "User with email {} already exists".format(email)}, 400

    new_user = UserModel(
        username=username, age=age, name=name, is_admin=is_admin, email=email,
        hashed_password=UserModel.generate_hash(password)
    )
    try:
        new_user.save_to_db()
        lst = []

        if new_user.is_admin:
            lst.append("admin")

        groups = {"groups": lst}

        access_token = create_access_token(identity=username, additional_claims=groups)
        refresh_token = create_refresh_token(identity=username, additional_claims=groups)
        return {
            "message": "User {} was created".format(username),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'groups': groups
        }
    except Exception as e:
        return {
                   "message": "Something went wrong while creating",
                   "error": repr(e)
               }, 500


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """Method for logination. Returns access and refresh tokens."""
    if not request.json or not request.json.get("username") or not request.json.get("password"):
        return jsonify({"message": 'Please, provide "username" and "password" in body.'}), 400

    username = request.json["username"]
    password = request.json["password"]
    current_user_ = UserModel.find_by_username(username, to_dict=False)
    if not current_user_:
        return {"message": "User {} doesn't exist".format(username)}
    lst = []

    if current_user_.is_admin:
        lst.append("admin")

    groups = {"groups": lst}

    if UserModel.verify_hash(password, current_user_.hashed_password):
        access_token = create_access_token(identity=username, additional_claims=groups)
        refresh_token = create_refresh_token(identity=username, additional_claims=groups)
        return {
            "message": "Logged in as {}".format(current_user_.username),
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    else:
        return {"message": "Wrong password"}, 401


@auth_bp.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def post():
    """Method for refreshing access token. Returns new access token."""
    current_user_identity = get_jwt_identity()
    username = get_jwt().get("sub", [])
    current_user_ = UserModel.find_by_username(username, to_dict=False)
    if not current_user_:
        return {"message": "User {} doesn't exist".format(username)}
    lst = []

    if current_user_.is_admin:
        lst.append("admin")

    groups = {"groups": lst}
    access_token = create_access_token(identity=current_user_identity, additional_claims=groups)
    return {'access_token': access_token}


@auth_bp.route("/auth/logout-access", methods=["POST"])
@jwt_required()
def logout_access():
    jti = get_jwt()['jti']
    try:
        revoked_token = RevokedTokenModel(jti=jti)
        revoked_token.add()
        return {'message': 'Access token has been revoked'}
    except Exception as e:
        return {
                   "message": "Something went wrong while revoking token",
                   "error": repr(e)
               }, 500


@auth_bp.route("/auth/logout-refresh", methods=["POST"])
@jwt_required(refresh=True)
def logout_refresh():
    jti = get_jwt()['jti']  # id of a jwt accessing this post method
    try:
        revoked_token = RevokedTokenModel(jti=jti)
        revoked_token.add()
        return {"message": "Refresh token has been revoked"}
    except Exception:
        return {"message": "Something went wrong while revoking token"}, 500


@auth_bp.route("/auth/change-password", methods=["PATCH"])
@jwt_required()
def update_password():
    email = request.json.get("email")
    password = request.json.get("password")
    new_password = request.json.get("new_password")
    user = UserModel.find_by_email(email, to_dict=False)
    if not user:
        return jsonify({"message": "User not found."}), 404
    if new_password:
        if user.verify_hash(password, user.hashed_password):

            user.hashed_password = UserModel.generate_hash(new_password)
            user.save_to_db()
            return {"message": "Password changed successfully"}
        else:
            return {"message": "Incorrect password"}, 400
    else:
        return {"message": "Field 'new_password' is empty"}
