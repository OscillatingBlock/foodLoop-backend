from flask import Blueprint, request, jsonify
from flask_security.utils import hash_password, verify_password, login_user, logout_user
from flask_security.decorators import auth_required
from flask_login import current_user
from .models import db, User, Role
from flask import current_app
import jwt
from datetime import datetime, timedelta, timezone
from flask_security.datastore import (
    SQLAlchemyUserDatastore,
)

# # Initialize user_datastore within the route or use app context
# def get_user_datastore():
#     return SQLAlchemyUserDatastore(db, User, None)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400

    if current_app.extensions["security"].datastore.find_user(username=username):
        return jsonify({"error": "Username already exists, please choose another"}), 409

    if user_datastore.find_user(email=email):
        return (
            jsonify(
                {
                    "error": "Email address is already registered, you might want to log in instead"
                }
            ),
            409,
        )

    user = user_datastore.create_user(
        username=username, email=email, password=hash_password(password), userRole=role
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    remember = data.get("remember", False)

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = user_datastore.find_user(email=email)
    role = user.userRole if user else None

    if user and verify_password(password, user.password):
        login_user(user, remember=remember)
        expiration_time = datetime.now(timezone.utc) + timedelta(hours=1)
        payload = {
            "user_id": user.id,
            "email": user.email,
            "role": role,
            "exp": expiration_time,
        }
        jwt_token = jwt.encode(
            payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256"
        )

        return jsonify({"message": "Login successful", "token": jwt_token}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@auth_bp.route("/auth/status", methods=["GET"])
def status():
    if current_user.is_authenticated:
        user_data = {
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.userRole,
        }
        return jsonify({"authenticated": True, "user": user_data}), 200
    else:
        return jsonify({"authenticated": False}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout_api():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200
