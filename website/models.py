from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(50))
    notes = db.relationship('Recipe')

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipe_name = db.Column(db.String(200))
    prep_time = db.Column(db.Integer, primary_key=False)
    cook_time = db.Column(db.Integer, primary_key=False)
    ingredients = db.Column(db.String())
    instructions = db.Column(db.String())
    original_url = db.Column(db.String())
