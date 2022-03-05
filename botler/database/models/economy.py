from botler.database import db


class Economy(db.Model):
    __tablename__ = "economy"

    guild_id = db.Column(db.BIGINT, primary_key=True)
    member_id = db.Column(db.BIGINT, primary_key=True)
    balance = db.Column(db.BIGINT, default=0)


class Item(db.Model):
    __tablename__ = "items"

    guild_id = db.Column(db.BIGINT, primary_key=True)
    name = db.Column(db.Text, primary_key=True)
    price = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, default=None)
    stock = db.Column(db.Integer, default=-1)
    role_required = db.Column(db.BIGINT, default=None)
    role_given = db.Column(db.BIGINT, default=None)
    role_removed = db.Column(db.BIGINT, default=None)
    required_balance = db.Column(db.BIGINT, default=0)
    reply = db.Column(db.Text, default=None)
