from app.database import db


class Task(db.Model):

    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)

    status = db.Column(db.String(20), nullable=False, default="pending")

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship(
        "User",
        back_populates="tasks"
    )

    def to_dict(self):

        return {"id": self.id, "title": self.title, "status": self.status}
