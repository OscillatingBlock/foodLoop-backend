from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from flask_security import UserMixin, RoleMixin
from sqlalchemy import Nullable

db = SQLAlchemy()

roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id")),
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(
        db.String(255), unique=True, nullable=False
    )  # Required by Flask-Security
    userRole = db.Column(db.String(20), nullable=False)
    roles = db.relationship(
        "Role", secondary="roles_users", backref=db.backref("users", lazy="dynamic")
    )
    surplus_food = db.relationship(
        "SurplusFood", backref="owner", lazy=True
    )  # Add this line


class SurplusFood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    food_name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.String(255), nullable=False)
    expiry = db.Column(db.String(255))
    location = db.Column(db.String(255))
    status = db.Column(db.String(20), nullable=False)


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surplus_food_id = db.Column(
        db.Integer, db.ForeignKey("surplus_food.id"), nullable=False
    )
    ngo_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    food_owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    request_date = db.Column(db.String(30))
    notes = db.Column(db.String(255))
    response_date = db.Column(db.String(30))
    pickup_date = db.Column(db.String(30))
    quantity = db.Column(db.String(255))
