from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    role = db.Column(db.String(80), nullable=False, default="User")
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "email": self.email, "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
