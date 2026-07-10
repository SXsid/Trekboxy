from datetime import date
from uuid import uuid4

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from extensions import db
from helper.cache import cache_delete
from helper.decorators import role_required
from models import Booking, TaskOutbox, Trek

bookings_bp = Blueprint("bookings", __name__)


@bookings_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("trekker")
def create_booking():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    trek_id = data.get("trek_id")
    if not trek_id:
        return jsonify({"error": "trek_id is required"}), 400

    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"error": "Trek not found"}), 404

    if trek.status != "Open":
        return (
            jsonify(
                {
                    "error": "Trek is not open for bookings",
                    "current_status": trek.status,
                }
            ),
            400,
        )

    if trek.available_slots <= 0:
        return jsonify({"error": "No slots available — trek is full"}), 400

    existing = Booking.query.filter_by(user_id=user_id, trek_id=trek_id).first()
    if existing:
        return jsonify({"error": "You have already booked this trek"}), 409

    booking = Booking(
        user_id=user_id,
        trek_id=trek_id,
        status="Booked",  # immediately Booked — no approval step
    )
    trek.available_slots -= 1

    db.session.add(booking)

    try:
        db.session.commit()
        # unique constriant voilaton
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Booking already exists (race condition caught)"}), 409

    cache_delete("treks:all", f"treks:{trek_id}")

    return (
        jsonify({"message": "Trek booked successfully"}),
        201,
    )


@bookings_bp.route("/", methods=["GET"])
@jwt_required()
def get_my_bookings():
    user_id = int(get_jwt_identity())

    bookings = (
        Booking.query.filter_by(user_id=user_id)
        .order_by(Booking.booking_date.desc())
        .all()
    )

    result = []
    for b in bookings:
        d = b.to_dict()
        d["trek"] = b.trek.to_dict() if b.trek else None
        result.append(d)

    return jsonify({"bookings": result}), 200


@bookings_bp.route("/<int:booking_id>/cancel", methods=["PUT"])
@jwt_required()
@role_required(["admin", "trekker"])
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    if booking.user_id != user_id:
        return jsonify({"error": "Forbidden — not your booking"}), 403

    if booking.status == "Cancelled":
        return jsonify({"error": "Already cancelled"}), 400

    trek = booking.trek
    if not trek:
        return (
            jsonify({"message": "Trek itself is either cancelled or unavailable "}),
            200,
        )
    if trek.status != "open":
        return jsonify({"error": "Cancellation window is closed"}), 403

    if trek:
        trek.available_slots += 1

    booking.status = "Cancelled"
    db.session.commit()

    if trek:
        cache_delete("treks:all", f"treks:{trek.id}")

    return jsonify({"message": "Booking cancelled", "booking": booking.to_dict()}), 200


@bookings_bp.route("/export", methods=["GET"])
@jwt_required()
@role_required("trekker")
def export_bookings_csv():
    user_id = int(get_jwt_identity())
    today = date.today().isoformat()

    idempotency_key = f"csv_export:{user_id}:{uuid4()}"

    # existing = TaskOutbox.query.filter_by(idempotency_key=idempotency_key).first()
    # if existing:
    #     return (
    #         jsonify(
    #             {
    #                 "message": "Export already queued. You already have or  will receive an email shortly.",
    #             }
    #         ),
    #         200,
    #     )

    task = TaskOutbox(
        idempotency_key=idempotency_key,
        task_type="CSV_EXPORT",
        payload={"user_id": user_id},
        status="PENDING",
    )
    db.session.add(task)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "Export queued. You will receive an email when it's ready.",
                "task_id": task.id,
            }
        ),
        202,
    )
