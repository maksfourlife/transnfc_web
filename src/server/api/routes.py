from flask import Blueprint, jsonify, request
from flask_bcrypt import generate_password_hash, check_password_hash
from .. import db, User, Transaction, Chip, generate_token
import datetime as dt

api = Blueprint("api", __name__)


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

    try:
        user = User.query.filter_by(login=login_email).first() or User.query.filter_by(email=login_email).first()
        if not user:
            return jsonify({"success": False, "message": "No such login or email"}), 200

        if not check_password_hash(user.password, password):
            return jsonify({"success": False, "message": "Incorrect password"}), 200

        return jsonify({"success": True, "id": user.id, "first": user.first, "last": user.last, "login": user.login, "email": user.email, "wallet": user.wallet}), 200
    except Exception as e:
        return str(e)


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


@api.route("/get_payments", methods=["POST", "GET"])
def get_payments():
    try:
        id = request.form["id"]
        amount = request.form["amount"]
    except:
        return jsonify({"success": False, "message": "Corrupted data"}), 200

    user = User.query.get(id)
    if not user:
        return jsonify({"success": False, "message": "No such Id"}), 200

    payments = Transaction.query.filter_by(user_id=user.id).filter_by(type=0).order_by(Transaction.time.desc()).limit(amount).all()
    return jsonify({"success": True, "payments": [
        {"time": payment.time.timestamp(), "route": payment.route.name if payment.route else None, "amount": payment.amount} for payment in payments
    ]}), 200


@api.route("/get_transactions", methods=["POST", "GET"])
def get_transactions():
    try:
        id = request.form["id"]
        amount = request.form["amount"]
    except:
        return jsonify({"success": False, "message": "Corrupted data"}), 200

    user = User.query.get(id)
    if not user:
        return jsonify({"success": False, "message": "No such Id"}), 200

    payments = Transaction.query.filter_by(user_id=user.id).filter_by(type=1).order_by(Transaction.time.desc()).limit(amount).all()
    return jsonify({"success": True, "payments": [
        {"time": payment.time.timestamp(), "amount": payment.amount} for payment in payments
    ]}), 200


@api.route('/generate_token', methods=['POST', 'GET'])
def _generate_token():
    return generate_token(), 200


@api.route('/pay', methods=['POST'])
def pay():
    try:
        id = request.form['id']
        key = request.form['key']
    except:
        return jsonify({'success': False, 'message': 'Corrupted data'}), 200

    user = User.query.get(id)
    if not user:
        return jsonify({"success": False, "message": "No such Id"}), 200

    chip = Chip.query.filter_by(key=key).first()
    if not chip:
        return jsonify({'success': False, 'message': 'No such chip'}), 200

    holding = chip.transport.holding.query.first()
    if not holding:
        return jsonify({'success': False, 'message': 'No such holding'}), 200

    price = holding.normal
    last_payment = user.transactions.filter_by(type=0).filter_by(amount=price).order_by(Transaction.time.desc()).first()
    if last_payment and dt.datetime.now().timestamp() - last_payment.time.timestamp() <= holding.discount_seconds:
        price = holding.discount
    user.wallet -= price

    transaction = Transaction(amount=price, type=0)
    user.transactions.append(transaction)
    chip.transport.transactions.append(transaction)
    chip.transport.route.transactions.append(transaction)

    db.session.commit()

    return jsonify({'success': True}), 200

