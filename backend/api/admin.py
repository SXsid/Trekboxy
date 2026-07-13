from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from helper.cache import TTL_ADMIN_STATS, cache_get, cache_set
from helper.decorators import role_required
from models import Booking, Trek, User

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@role_required("admin")
def dashboard():
    cached = cache_get("admin:stats")
    if cached:
        return jsonify({"stats": cached}), 200

    stats = {
        "total_users": User.query.filter_by(role="trekker").count(),
        "total_staff": User.query.filter_by(role="staff").count(),
        "total_treks": Trek.query.count(),
        "open_treks": Trek.query.filter_by(status="Open").count(),
        "total_bookings": Booking.query.count(),
        "active_bookings": Booking.query.filter_by(status="Booked").count(),
    }

    cache_set("admin:stats", stats, TTL_ADMIN_STATS)

    return jsonify({"stats": stats}), 200


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@role_required("admin")
def list_users():
    role_filter = request.args.get("role")
    search = request.args.get("search")

    query = User.query.filter(User.role != "admin")

    if role_filter:
        query = query.filter_by(role=role_filter)

    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
        )

    users = query.all()
    return jsonify({"users": [u.to_dict() for u in users]}), 200


@admin_bp.route("/treks", methods=["GET"])
@jwt_required()
@role_required("admin")
def admin_list_treks():
    status_filter = request.args.get("status")
    search = request.args.get("search")

    query = Trek.query

    if status_filter:
        query = query.filter_by(status=status_filter)

    if search:
        query = query.filter(
            db.or_(
                Trek.name.ilike(f"%{search}%"),
                Trek.location.ilike(f"%{search}%"),
            )
        )

    treks = query.order_by(Trek.created_at.desc()).all()

    result = []
    for t in treks:
        d = t.to_dict()
        d["booking_count"] = Booking.query.filter_by(
            trek_id=t.id, status="Booked"
        ).count()
        result.append(d)

    return jsonify({"treks": result}), 200


@admin_bp.route("/users/<int:user_id>/status", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update_user_status(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role == "admin":
        return jsonify({"error": "Cannot modify admin accounts"}), 403

    data = request.get_json()

    if "is_active" in data:
        user.is_active = bool(data["is_active"])
    if "is_blacklisted" in data:
        user.is_blacklisted = bool(data["is_blacklisted"])
        if data["is_blacklisted"]:
            user.is_active = False

    db.session.commit()

    return jsonify({"message": "User status updated", "user": user.to_dict()}), 200


@admin_bp.route("/staff", methods=["POST"])
@jwt_required()
@role_required("admin")
def create_staff():
    data = request.get_json()

    required = ["username", "email", "password", "phone"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"'{field}' is required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already in use"}), 409

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already taken"}), 409

    staff = User(
        username=data["username"],
        email=data["email"],
        role="staff",
        full_name=data.get("full_name", ""),
        phone=data.get("phone", ""),
        is_active=True,
    )
    staff.set_password(data["password"])

    db.session.add(staff)
    db.session.commit()

    return jsonify({"message": "Staff account created", "user": staff.to_dict()}), 201


@admin_bp.route("/bookings", methods=["GET"])
@jwt_required()
@role_required("admin")
def list_all_bookings():
    trek_filter = request.args.get("trek_id")
    status_filter = request.args.get("status")

    query = Booking.query

    if trek_filter:
        query = query.filter_by(trek_id=int(trek_filter))
    if status_filter:
        query = query.filter_by(status=status_filter)

    bookings = query.order_by(Booking.booking_date.desc()).all()

    result = []
    for b in bookings:
        d = b.to_dict()
        d["trek"] = b.trek.to_dict() if b.trek else None
        d["user"] = b.trekker.to_dict() if b.trekker else None
        result.append(d)

    return jsonify({"bookings": result}), 200
