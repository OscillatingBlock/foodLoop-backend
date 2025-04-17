from flask import Blueprint, request, jsonify
from flask_security.decorators import auth_required
from flask_login import current_user
from .models import db, SurplusFood, Request, User
from datetime import datetime, timedelta

requests_bp = Blueprint("requests", __name__)


@requests_bp.route("/surplus/<int:id>/request", methods=["POST"])
@auth_required()
def send_request(id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    quantity = data.get("quantity")
    notes = data.get("notes")
    pickup_date = data.get("pickup_date")
    ngo_id = current_user.id

    if not quantity:
        return jsonify({"error": "Quantity is required"}), 400

    if not ngo_id:
        return jsonify({"error": "NGO ID is required"}), 400

    food_item = SurplusFood.query.get(id)
    if not food_item:
        return jsonify({"error": "Food item not found"}), 404

    req = Request(
        quantity=quantity,
        ngo_id=ngo_id,
        surplus_food_id=id,
        notes=notes,
        pickup_date=pickup_date,
        food_owner_id=food_item.user_id,
    )

    db.session.add(req)
    db.session.commit()
    return jsonify({"status": "Request added successfully"}), 201


@requests_bp.route("/requests", methods=["GET"])
@auth_required()
def get_requests():
    request_type = request.args.get("type", "received")

    if request_type == "made" and current_user.userRole == "NGO":
        requests = Request.query.filter_by(ngo_id=current_user.id).all()
    elif request_type == "received" and current_user.userRole in ["Farmer", "Retailer"]:
        requests = Request.query.filter_by(food_owner_id=current_user.id).all()
    else:
        return jsonify({"error": "Invalid request type for user role"}), 400

    req_lists = []
    for request in requests:
        req_lists.append(
            {
                "id": request.id,
                "food_name": request.surplus_food.food_name,
                "quantity": request.quantity,
                "notes": request.notes,
                "pickup_date": request.pickup_date,
                "response_date": request.response_date,
                "request_date": request.request_date,
                "provider_id": request.food_owner_id,
                "provider_name": request.food_owner.user_name,
                "requester_id": request.ngo_id,
                "requester_name": request.ngo.user_name,
                "status": request.status,
            }
        )

    return jsonify(req_lists), 200
