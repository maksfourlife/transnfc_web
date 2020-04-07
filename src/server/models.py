from . import db, generate_token
from datetime import datetime
from secrets import token_bytes

_DT_PATTERN = "%A, %d. %B %Y %H:%M"


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)

    first = db.Column(db.String(20), nullable=False)
    last = db.Column(db.String(20), nullable=False)
    login = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    wallet = db.Column(db.Integer, default=0, nullable=False)

    reg_dt = db.Column(db.DateTime, default=datetime.now, nullable=False)
    confirmed = db.Column(db.Boolean, default=False, nullable=False)

    profile_image = db.relationship("Image", backref="user", uselist=False)
    admin = db.relationship("Admin", backref="user", uselist=False)
    driver = db.relationship("Driver", backref="user", uselist=False)
    transactions = db.relationship("Transaction", backref="user", lazy="dynamic")

    def __repr__(self):
        return f"\nId: {self.id}\n" \
               f"First&Last: {self.first} {self.last}\n" \
               f"Email: {self.email}\n" \
               f"Registered on: {self.reg_dt.strftime(_DT_PATTERN)}\n"


class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    holding_id = db.Column(db.Integer, db.ForeignKey("holding.id"))

    passport_image = db.relationship("Image", backref="admin")
    key = db.relationship("AdminKey", backref="admin", uselist=False)
    requests = db.relationship("Request", backref="request", lazy="dynamic")

    def __repr__(self):
        return f"\nId: {self.id}\n" \
               f"Type: {self.type}\n" \
               f"Key: {self.key.key if self.key else None}\n" \
               f"UserId: {self.user_id}\n"


class AdminKey(db.Model):
    __tablename__ = "adminkey"
    id = db.Column(db.Integer, primary_key=True)

    key = db.Column(db.String(64), default=generate_token, nullable=False)
    activated = db.Column(db.Boolean, default=0, nullable=False)

    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))

    def __repr__(self):
        return f"\nId: {self.id}\n" \
               f"Key: {self.key}\n" \
               f"Activated: {self.activated}\n" \
               f"Admin Id: {self.admin_id}\n"


class Driver(db.Model):
    __tablename__ = "driver"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    transport_id = db.Column(db.Integer, db.ForeignKey("transport.id"))
    holding_id = db.Column(db.Integer, db.ForeignKey("holding.id"))

    start_time = db.Column(db.DateTime, nullable=True)
    finish_time = db.Column(db.DateTime, nullable=True)

    started = db.Column(db.DateTime, nullable=True)
    finished = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"\nId: {self.id}\n" \
               f"Start/Finish: {self.start_time if self.start_time else '00:00'}/{self.finish_time if self.finish_time else '00:00'}\n" \
               f"Started/Finished: {self.started if self.started else '00:00'}/{self.finished if self.finished else '00:00'}\n" \
               f"TransportId: {self.transport_id}\n" \
               f"HoldingId: {self.holding_id}\n" \
               f"UserId: {self.user_id}\n"


class Image(db.Model):
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)

    data = db.Column(db.LargeBinary, nullable=False)
    ext = db.Column(db.String(5), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))

    def __repr__(self):
        return f"\nId: {self.id}\n" \
               f"See: https://www.transnfc.com/seeimage?id={self.id}\n"


class Holding(db.Model):
    __tablename__ = "holding"
    id = db.Column(db.Integer, primary_key=True)

    bill = db.Column(db.String(200), nullable=False)
    legal_entity = db.Column(db.String(200), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    city_town = db.Column(db.String(100), nullable=False)

    normal_ground = db.Column(db.Integer, nullable=False)
    discount_ground = db.Column(db.Integer, nullable=False)
    normal_underground = db.Column(db.Integer, nullable=False)
    discount_underground = db.Column(db.Integer, nullable=False)
    # TODO remove underground prices
    discount_seconds = db.Column(db.Integer, default=0, nullable=False)

    drivers = db.relationship("Driver", backref="holding", lazy="dynamic")
    admins = db.relationship("Admin", backref="holding", lazy="dynamic")
    transports = db.relationship("Transport", backref="holding", lazy="dynamic")
    requests = db.relationship("Request", backref="holding", lazy="dynamic")
    routes = db.relationship("Route", backref="holding", lazy="dynamic")

    def __repr__(self):
        return f"\nId: {self.id}\n" \
               f"Bill: {self.bill}\n" \
               f"Legal entity: {self.legal_entity}\n" \
               f"Prices:\n" \
               f"\tDiscount seconds: {self.discount_seconds}\n" \
               f"\tGround:\n" \
               f"\t\tNormal: {self.normal_ground}\n" \
               f"\t\tDiscount: {self.discount_ground}\n" \
               f"\tUnderground:\n" \
               f"\t\tNormal: {self.normal_underground}\n" \
               f"\t\tDiscount: {self.discount_underground}\n"


class Transport(db.Model):
    __tablename__ = "transport"
    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.Integer, nullable=False)
    # TODO add name

    route_id = db.Column(db.Integer, db.ForeignKey("route.id"))
    holding_id = db.Column(db.Integer, db.ForeignKey("holding.id"))

    driver = db.relationship("Driver", backref="transport", uselist=False)
    transactions = db.relationship("Transaction", backref="transport", lazy="dynamic")
    chips = db.relationship("Chip", backref="transport")

    def __repr__(self):
        return f"\nId: {self.id}\n" \
               f"Type: {self.type}\n" \
               f"Route Id: {self.route_id}\n" \
               f"Holding Id: {self.holding_id}\n"


class Chip(db.Model):
    __tablename__ = "chip"
    id = db.Column(db.Integer, primary_key=True)

    key = db.Column(db.String(32), nullable=False)
    installed = db.Column(db.Boolean, default=False, nullable=False)

    transport_id = db.Column(db.Integer, db.ForeignKey("transport.id"))
    request_id = db.Column(db.Integer, db.ForeignKey("request.id"))

    def __repr__(self):
        return f"\nId: {self.id}\n" \
               f"Installed: {self.installed}\n" \
               f"Transport Id: {self.transport_id}\n" \
               f"Request Id: {self.request_id}\n"


class Request(db.Model):
    __tablename__ = "request"
    id = db.Column(db.Integer, primary_key=True)

    state = db.Column(db.String(200), nullable=True)
    order_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))
    holding_id = db.Column(db.Integer, db.ForeignKey("holding.id"))

    chips = db.relationship("Chip", backref="request", lazy="dynamic")

    def __repr__(self):
        return f"\nId: {self.id}\n" \
               f"State: {self.state}\n" \
               f"Order time: {self.order_time.strftime(_DT_PATTERN)}\n" \
               f"Admin Id: {self.admin_id}\n" \
               f"Holding Id: {self.holding_id}\n"


class Route(db.Model):
    __tablename__ = "route"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(5), nullable=False)

    holding_id = db.Column(db.Integer, db.ForeignKey("holding.id"))

    transports = db.relationship("Transport", backref="route", lazy="dynamic")
    transactions = db.relationship("Transaction", backref="route", lazy="dynamic")

    def __repr__(self):
        return f"\nId: {self.id}\n" \
               f"Name: {self.name}\n" \
               f"Holding Id: {self.holding_id}\n"


class Transaction(db.Model):
    __tablename__ = "transaction"
    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, default=datetime.now, nullable=False)

    transport_id = db.Column(db.Integer, db.ForeignKey("transport.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    route_id = db.Column(db.Integer, db.ForeignKey("route.id"))

    def __repr__(self):
        return f"\nId: {self.id}\n" \
               f"Amount: {self.amount}\n" \
               f"Type: {self.type}\n" \
               f"Time: {self.time.strftime(_DT_PATTERN)}\n" \
               f"Transport Id: {self.transport_id}\n" \
               f"User Id: {self.user_id}\n"
