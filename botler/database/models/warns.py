import datetime

from botler.database import db


class Warn(db.Model):
    __tablename__ = "warns"

    id = db.Column(db.BIGINT, primary_key=True)
    guild_id = db.Column(db.BIGINT)
    user_id = db.Column(db.BIGINT)
    reason = db.Column(db.Text)
    moderator = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
