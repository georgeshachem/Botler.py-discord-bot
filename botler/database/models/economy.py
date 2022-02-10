from botler.database import db


class Economy(db.Model):
    __tablename__ = "economy"

    guild_id = db.Column(db.BIGINT, primary_key=True)
    member_id = db.Column(db.BIGINT, primary_key=True)
    balance = db.Column(db.BIGINT, default=0)
