from flask import Blueprint, jsonify, request
from flask_bcrypt import generate_password_hash, check_password_hash
from .. import db, User

api = Blueprint(__name__, "api")


@api.route("/register", methods=["POST", "GET"])
def register():
    try:
        first = request.form["first"]
        last = request.form["last"]
        login = request.form["login"]
        email = request.form["email"]
        password = request.form["pwd"]
    except:
        return jsonify({"success": False, "message": "Corrupted data"}), 200

    if len(User.query.filter_by(login=login).all()):
        return jsonify({"success": False, "message": "Login already taken"}), 200

    if len(User.query.filter_by(email=email).all()):
        return jsonify({"success": False, "message": "Email already taken"}), 200

    db.session.add(User(first=first, last=last, login=login, email=email, password=generate_password_hash(password)))
    db.session.commit()

    user = User.query.filter_by(login=login).first()
    return jsonify({"success": True, "id": user.id}), 200


@api.route("/login", methods=["POST", "GET"])
def login():
    try:
        login_email = request.form["login_email"]
        password = request.form["pwd"]
    except:
        return jsonify({"success": False, "message": "Corrupted data"})

    user = User.query.filter_by(login=login_email).first() or User.query.filter_by(email=login_email).first()
    if not user:
        return jsonify({"success": False, "message": "No such login or email"}), 200

    if not check_password_hash(user.password, password):
        return jsonify({"success": False, "message": "Incorrect password"}), 200

    return jsonify({"success": True, "id": user.id, "first": user.first, "last": user.last, "login": user.login, "email": user.email, "wallet": user.wallet}), 200


@api.route("/get_wallet", methods=["POST", "GET"])
def get_wallet():
    try:
        id = request.form["id"]
    except:
        return jsonify({"success": False, "message": "Corrupted data"}), 200

    user = User.query.get(id)
    if not user:
        return jsonify({"success": False, "message": "No such Id"}), 200

    return jsonify({"success": True, "wallet": user.wallet}), 200
