from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)