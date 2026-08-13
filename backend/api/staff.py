from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from helper.cache import cache_delete
from helper.decorators import role_required
from logger import get_logger
from models import Booking, Trek, User

logger = get_logger(__name__)
staff_bp = Blueprint("staff", __name__)
STAFF_ALLOWED_STATUSES = {"Open", "Closed", "Completed"}

@staff_bp.route("/treks", methods=["GET"])
@jwt_required()
@role_required("staff")
def get_assigned_treks():
    staff_id = int(get_jwt_identity())
    try:
        treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()
        result = []
        for t in treks:
            d = t.to_dict()
            d["booking_count"] = Booking.query.filter_by(trek_id=t.id, status="Booked").count()
            result.append(d)
    except SQLAlchemyError:
        logger.exception("DB error fetching assigned treks: staff_id=%s", staff_id)
        return jsonify({"error": "Failed to fetch assigned treks"}), 500
    return jsonify({"treks": result}), 200

@staff_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@jwt_required()
@role_required("staff")
def update_trek_status(trek_id):
    staff_id = int(get_jwt_identity())
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"error": "Trek not found"}), 404
    if trek.assigned_staff_id != staff_id:
        logger.warning("Staff ownership violation: staff_id=%s trek_id=%s", staff_id, trek_id)
        return jsonify({"error": "You are not assigned to this trek"}), 403
    data = request.get_json()
    try:
        if "status" in data:
            if data["status"] not in STAFF_ALLOWED_STATUSES:
                return jsonify({"error": f"Staff can only set status to: {STAFF_ALLOWED_STATUSES}"}), 400
            trek.status = data["status"]
        if "slots" in data:
            slots = int(data["slots"])
            if slots < 0:
                return jsonify({"error": "Slots cannot be negative"}), 400
            trek.total_slots = slots
        db.session.commit()
        logger.info("Trek status updated by staff: trek_id=%s staff_id=%s", trek_id, staff_id)
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("DB error updating trek status: trek_id=%s", trek_id)
        return jsonify({"error": "Failed to update trek"}), 500
    cache_delete("treks:all", f"treks:{trek_id}")
    return jsonify({"message": "Trek updated"}), 200

@staff_bp.route("/treks/<int:trek_id>/participants", methods=["GET"])
@jwt_required()
@role_required("staff")
def get_participants(trek_id):
    staff_id = int(get_jwt_identity())
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"error": "Trek not found"}), 404
    if trek.assigned_staff_id != staff_id:
        logger.warning("Staff tried to view participants for unassigned trek: staff_id=%s trek_id=%s", staff_id, trek_id)
        return jsonify({"error": "You are not assigned to this trek"}), 403
    try:
        bookings = Booking.query.filter_by(trek_id=trek_id).filter(Booking.status != "Cancelled").all()
        participants = []
        for b in bookings:
            p = b.to_dict()
            p["user"] = b.trekker.to_dict() if b.trekker else None
            participants.append(p)
    except SQLAlchemyError:
        logger.exception("DB error fetching participants: trek_id=%s", trek_id)
        return jsonify({"error": "Failed to fetch participants"}), 500
    return jsonify({"trek": trek.to_dict(), "participants": participants, "count": len(participants)}), 200
