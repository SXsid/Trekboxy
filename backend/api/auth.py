from datetime import timedelta

from extensions import db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from logger import get_logger
from models import User
from sqlalchemy.exc import SQLAlchemyError

logger = get_logger(__name__)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    required = ["username", "email", "password", "phone"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"\'{field}\' is required"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already taken"}), 409
    user = User(
        username=data["username"],
        email=data["email"],
        role="trekker",
        full_name=data.get("full_name", ""),
        phone=data.get("phone", ""),
    )
    user.set_password(data["password"])
    try:
        db.session.add(user)
        db.session.commit()
        logger.info("New trekker registered: %s (id=%s)", user.username, user.id)
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("DB error while registering user: %s", data.get("username"))
        return jsonify({"error": "Registration failed due to a database error"}), 500
    return jsonify({"message": "Registration successful", "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        logger.warning("Failed login attempt for email: %s", data.get("email"))
        return jsonify({"error": "Invalid credentials"}), 401
    if user.is_blacklisted:
        logger.warning("Blacklisted user login attempt: %s (id=%s)", user.username, user.id)
        return jsonify({"error": "Account is blacklisted"}), 403
    TOKEN_EXPIRY_BY_ROLE = {
        "admin": False,
        "staff": timedelta(days=1),
        "trekker": timedelta(hours=12),
    }
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
        expires_delta=TOKEN_EXPIRY_BY_ROLE.get(user.role, timedelta(hours=12)),
    )
    logger.info("User logged in: %s (role=%s, id=%s)", user.username, user.role, user.id)
    return jsonify({"access_token": token, "user": user.to_dict()}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        logger.warning("GET /me — user not found: id=%s", user_id)
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200


@auth_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        logger.warning("PUT /me — user not found: id=%s", user_id)
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    if "full_name" in data:
        user.full_name = data["full_name"]
    if "phone" in data:
        user.phone = data["phone"]
    if "new_password" in data and data["new_password"]:
        if not data.get("current_password"):
            return jsonify({"error": "Current password is required to change password"}), 400
        if not user.check_password(data["current_password"]):
            logger.warning("Incorrect current password attempt: user_id=%s", user_id)
            return jsonify({"error": "Incorrect current password"}), 401
        user.set_password(data["new_password"])
    try:
        db.session.commit()
        logger.info("Profile updated: user_id=%s", user_id)
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("DB error while updating profile: user_id=%s", user_id)
        return jsonify({"error": "Profile update failed due to a database error"}), 500
    return jsonify({"message": "Profile updated", "user": user.to_dict()}), 200
