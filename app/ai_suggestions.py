from flask import Blueprint, request, jsonify
from flask_security.decorators import auth_required
from flask_login import current_user
from .models import db, SurplusFood, Request, User
from datetime import datetime, timedelta


ai_suggestions_bp = Blueprint("ai_predictions", __name__)


@ai_suggestions_bp.route("/ai_predictions/opportunity_alerts", methods=["GET"])
@auth_required()
def get_opportunity_alerts():
    if current_user.userRole != "NGO":
        return jsonify({"error": "Unauthorized access"}), 403

    ngo_location = current_user.location

    if not ngo_location:
        return jsonify({"error": "NGO location not set"}), 400

    # define time window(last 24 hours)
    time_threshold = datetime.utcnow() - timedelta(hours=24)

    # recent listings in last 24 hours
    recent_listings = (
        SurplusFood.query.join(User)
        .filter(
            SurplusFood.created_at > time_threshold,
            SurplusFood.status == "available",
            User.userRole.in_(["Farmer", "Retailer"]),
            SurplusFood.location.ilike(f"%{ngo_location}%"),
        )
        .all()
    )

    # Identify unique farmers (based on user_id)
    farmer_ids = set(listing.user_id for listing in recent_listings)
    farmer_count = len(farmer_ids)

    if farmer_count == 0:
        return (
            jsonify(
                {"suggestion": "No new surplus grains listed in your area recently."}
            ),
            200,
        )

    return (
        jsonify(
            {
                "opportunity_alert": f"{farmer_count} New farmers in your area have listed surplus in past 24 hours.",
                "farmer_count": "farmer_count",
            }
        ),
        200,
    )
