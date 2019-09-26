from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Penalty(db.Model):
    __tablename__ = 'penalty'

    id = db.Column(db.String(), primary_key=True)
    data_controller = db.Column(db.String(), unique=False, nullable=False)
    sector = db.Column(db.String(), unique=False, nullable=False)
    nature = db.Column(db.String(), unique=False, nullable=False)
    date = db.Column(db.DateTime(timezone=False), unique=False, nullable=False)
    fine = db.Column(db.Integer, unique=False, nullable=False)
    currency = db.Column(db.String(), unique=False, nullable=False)
    notes = db.Column(db.Integer, unique=False, nullable=True)

    def __repr__(self):
        return '<Penalty id: %s>' % self.id
