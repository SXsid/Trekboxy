from datetime import date

from extensions import db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from helper.cache import TTL_TREK_ONE, TTL_TREKS_ALL, cache_delete, cache_get, cache_set
from helper.decorators import role_required
from models import Booking, Trek

treks_bp = Blueprint("treks", __name__)

VALID_DIFFICULTIES = {"Easy", "Moderate", "Hard"}
VALID_STATUSES = {"Pending", "Approved", "Open", "Closed", "Completed"}


@treks_bp.route("/", methods=["GET"])
@jwt_required()
def list_treks():
    cached = cache_get("treks:all")
    if cached:
        return jsonify({"treks": cached}), 200

    # can't book trek which iss not open
    treks = Trek.query.filter(Trek.status.in_(["Approved", "Open"])).all()
    data = [t.to_dict() for t in treks]

    cache_set("treks:all", data, TTL_TREKS_ALL)

    return jsonify({"treks": data}), 200


@treks_bp.route("/search", methods=["GET"])
@jwt_required()
def search_treks():
    query = Trek.query.filter(Trek.status.in_(["Approved", "Open"]))

    difficulty = request.args.get("difficulty")
    location = request.args.get("location")
    duration = request.args.get("duration")

    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))
    if duration:
        query = query.filter_by(duration_days=int(duration))

    treks = query.all()
    return jsonify({"treks": [t.to_dict() for t in treks]}), 200


@treks_bp.route("/<int:trek_id>", methods=["GET"])
@jwt_required()
def get_trek(trek_id):
    cache_key = f"treks:{trek_id}"
    cached = cache_get(cache_key)
    if cached:
        return jsonify({"trek": cached}), 200

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"error": "Trek not found"}), 404

    data = trek.to_dict()
    cache_set(cache_key, data, TTL_TREK_ONE)

    return jsonify({"trek": data}), 200


@treks_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("admin")
def create_trek():
    data = request.get_json()
    user_id = int(get_jwt_identity())

    required = [
        "name",
        "location",
        "difficulty",
        "duration_days",
        "total_slots",
        "start_date",
        "end_date",
    ]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"'{field}' is required"}), 400

    trek = Trek(
        name=data["name"],
        location=data["location"],
        description=data.get("description", ""),
        difficulty=data["difficulty"],
        duration_days=data["duration_days"],
        total_slots=data["total_slots"],
        available_slots=data["total_slots"],
        status="Pending",
        start_date=date.fromisoformat(data["start_date"]),
        end_date=date.fromisoformat(data["end_date"]),
        registration_deadline=(
            date.fromisoformat(data["registration_deadline"])
            if data.get("registration_deadline")
            else date.fromisoformat(data["start_date"])
        ),
        price=data.get("price", 0.0),
        created_by=user_id,
    )

    db.session.add(trek)
    db.session.commit()

    # invalidate cache
    cache_delete("treks:all")

    return jsonify({"message": "Trek created", "trek": trek.to_dict()}), 201


@treks_bp.route("/<int:trek_id>", methods=["PUT"])
@jwt_required()
@role_required("admin")
def update_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"error": "Trek not found"}), 404

    data = request.get_json()

    if "name" in data:
        trek.name = data["name"]
    if "location" in data:
        trek.location = data["location"]
    if "description" in data:
        trek.description = data["description"]
    if "difficulty" in data:
        if data["difficulty"] not in VALID_DIFFICULTIES:
            return jsonify({"error": "Invalid difficulty"}), 400
        trek.difficulty = data["difficulty"]
    if "duration_days" in data:
        trek.duration_days = data["duration_days"]
    if "price" in data:
        trek.price = data["price"]
    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return jsonify({"error": "Invalid status"}), 400
        trek.status = data["status"]
    if "start_date" in data:
        trek.start_date = date.fromisoformat(data["start_date"])
    if "end_date" in data:
        trek.end_date = date.fromisoformat(data["end_date"])

    db.session.commit()

    cache_delete("treks:all", f"treks:{trek_id}")

    return jsonify({"message": "Trek updated"}), 200


@treks_bp.route("/<int:trek_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"error": "Trek not found"}), 404

    db.session.delete(trek)
    db.session.commit()

    cache_delete("treks:all", f"treks:{trek_id}")

    return jsonify({"message": "Trek deleted"}), 200


@treks_bp.route("/<int:trek_id>/assign", methods=["POST"])
@jwt_required()
@role_required("admin")
def assign_staff(trek_id):
    from models import User

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"error": "Trek not found"}), 404

    data = request.get_json()
    staff_id = data.get("staff_id")

    if not staff_id:
        return jsonify({"error": "staff_id is required"}), 400

    staff = User.query.get(staff_id)
    if not staff or staff.role != "staff":
        return jsonify({"error": "Invalid staff member"}), 400

    trek.assigned_staff_id = staff_id
    trek.status = "Approved"
    db.session.commit()

    cache_delete("treks:all", f"treks:{trek_id}")

    return (
        jsonify({"message": f"Staff {staff.username} assigned to trek {trek.name}"}),
        200,
    )
