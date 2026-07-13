from datetime import timedelta

from extensions import db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    required = ["username", "email", "password", "phone"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"'{field}' is required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409  # 409 Conflict

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already taken"}), 409

    user = User(
        username=data["username"],
        email=data["email"],
        role="trekker",  # INFO: slsf register is trekker by defulat
        full_name=data.get("full_name", ""),
        phone=data.get("phone", ""),
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return (
        jsonify({"message": "Registration successful", "user": user.to_dict()}),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    if user.is_blacklisted:
        return jsonify({"error": "Account is blacklisted"}), 403

    TOKEN_EXPIRY_BY_ROLE = {
        "admin": False,  # no expiry
        "staff": timedelta(days=1),
        "trekker": timedelta(hours=12),
    }

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
        expires_delta=TOKEN_EXPIRY_BY_ROLE.get(user.role, timedelta(hours=12)),
    )

    return jsonify({"access_token": token, "user": user.to_dict()}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200


@auth_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    if "full_name" in data:
        user.full_name = data["full_name"]
    if "phone" in data:
        user.phone = data["phone"]
    if "new_password" in data and data["new_password"]:
        if not data.get("current_password"):
            return (
                jsonify({"error": "Current password is required to change password"}),
                400,
            )
        if not user.check_password(data["current_password"]):
            return jsonify({"error": "Incorrect current password"}), 401
        user.set_password(data["new_password"])

    db.session.commit()

    return jsonify({"message": "Profile updated", "user": user.to_dict()}), 200
