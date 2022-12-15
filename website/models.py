from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(50))
    recipes = db.relationship('Recipe')


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, primary_key=False)
    username = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipe_name = db.Column(db.String(200))
    prep_time = db.Column(db.Integer, primary_key=False)
    cook_time = db.Column(db.Integer, primary_key=False)
    total_time = db.Column(db.Integer, primary_key=False)
    ingredients = db.Column(db.String())
    servings = db.Column(db.String())
    ingredients_quantity = db.Column(db.String())
    ingredients_measurement = db.Column(db.String())
    instructions = db.Column(db.String())
    original_url = db.Column(db.String())
    image = db.Column(db.String())
    ingredient_list = db.relationship('Ingredients')


class Ingredients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, primary_key=False)
    recipe = db.Column(db.Integer, db.ForeignKey('recipe.uuid'))
    ingredient = db.Column(db.String())


class ShoppingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shopping_item = db.Column(db.String())
