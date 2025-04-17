from flask import Blueprint, request, jsonify, current_app
from flask_security.decorators import auth_required
from flask_login import current_user
from .models import db, SurplusFood, User

surplus_bp = Blueprint("surplus", __name__)

@surplus_bp.route("/surplus", methods=["POST"])
@auth_required()
def add_surplus():
    data = request.get_json()

    if data is None:
        return jsonify({"error": "data is empty"}), 400

    name = data.get("foodName")
    quantity = data.get("quantity")
    expiry = data.get("expirationDate")
    location = data.get("location")

    if not all([name, quantity, location, expiry]):
        return jsonify({"error": "Missing required fields"}), 400

    foodItem = SurplusFood(
        food_name=name,
        quantity=quantity,
        location=location,
        expiry=expiry,
        status="available",
        user_id=current_user.id,
    )
    db.session.add(foodItem)
    db.session.commit()

    return jsonify({"added": True, "id": foodItem.id}), 201


@surplus_bp.route("/surplus", methods=["GET"])
@auth_required()
def get_surplus():
    foodItems = SurplusFood.query.filter_by(user_id=current_user.id)

    if not foodItems:
        return jsonify({"error": "food items not available"}), 404
    foodList = []

    for items in foodItems:
        foodList.append(
            {
                "id": items.id,
                "name": items.food_name,
                "quantity": items.quantity,
                "expiry": items.expiry,
                "location": items.location,
                "status": items.status,
            }
        )
    return jsonify(foodList), 200

@surplus_bp.route("/all-surplus", methods=["GET"])
@auth_required()
def get_all_surplus():
    if current_user.userRole != "NGO":
        return jsonify({"error": "Unauthorized access"}), 403
    
    term = request.args.get('term', '')
    location = request.args.get('location', '')
    
    query = SurplusFood.query.filter_by(status="available")
    
    if term:
        query = query.filter(SurplusFood.food_name.ilike(f'%{term}%'))
    if location:
        query = query.filter(SurplusFood.location.ilike(f'%{location}%'))
        
    food_items = query.all()
    
    if not food_items:
        return jsonify([]), 200
        
    food_list = []
    for item in food_items:
        provider = User.query.get(item.user_id)
        provider_name = provider.username if provider else "Unknown"
        
        food_list.append({
            "id": item.id,
            "name": item.food_name,
            "quantity": item.quantity,
            "expiry": item.expiry,
            "location": item.location,
            "status": item.status,
            "provider": provider_name
        })
        
    return jsonify(food_list), 200
