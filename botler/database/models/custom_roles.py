from botler.database import db


class CustomRole(db.Model):
    __tablename__ = "custom_roles"

    guild_id = db.Column(db.BIGINT, primary_key=True)
    role_id = db.Column(db.BIGINT, primary_key=True)
    icon_perm = db.Column(db.BOOLEAN, default=False)
