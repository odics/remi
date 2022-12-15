from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from flask_login import login_required, current_user
import json
from .models import Recipe, Ingredients, ShoppingList
from all_recipes_parser import allrecipes_parse
from . import db
import shortuuid

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short', category='error')
        else:
            flash('Note added.', category='success')

    recipes = Recipe.query.filter_by(username=current_user.id).all()
    shopping_list = ShoppingList.query.count()
    session['shopping_list'] = shopping_list
    return render_template("home.html", user=current_user, recipes=recipes, shopping_list=shopping_list)


@views.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        url = request.form.get('recipe_url')

        recipe = allrecipes_parse(url)

        session['user_id'] = current_user.id
        session['title'] = recipe.title
        session['prep'] = recipe.prep
        session['cook'] = recipe.cook
        session['rest'] = recipe.rest
        session['total'] = recipe.total
        session['servings'] = recipe.servings
        session['ingredients'] = recipe.ingredients
        session['instructions'] = recipe.instructions
        session['image'] = recipe.image
        session['ingredient_list'] = recipe.ingredient_list

        return render_template("list_recipe.html", user=current_user, title=recipe.title, prep=recipe.prep,
                               cook=recipe.cook,
                               rest=recipe.rest, total=recipe.total, servings=recipe.servings,
                               ingredients=recipe.ingredients, instructions=recipe.instructions, image=recipe.image)

    return render_template("add_recipe.html", user=current_user)


@views.route('/save_recipe', methods=['GET', 'POST'])
@login_required
def save_recipe_to_db():

    user_id = session.get('user_id', None)
    title = session.get('title', None)
    prep = session.get('prep', None)
    cook = session.get('cook', None)
    rest = session.get('rest', None)
    total = session.get('total', None)
    servings = session.get('servings', None)
    ingredients = session.get('ingredients', None)
    instructions = session.get('instructions', None)
    image = session.get('image', None)
    ingredient_list = session.get('ingredient_list', None)
    uuid = shortuuid.uuid()

    new_recipe = Recipe(username=user_id, prep_time=prep, cook_time=cook, ingredients=ingredients,
                        instructions=instructions, recipe_name=title, image=image, total_time=total, servings=servings,
                        uuid=uuid)

    db.session.add(new_recipe)
    db.session.commit()

    for ingredient in ingredient_list:
        ingredient = Ingredients(uuid=uuid, ingredient=ingredient)
        db.session.add(ingredient)
        db.session.commit()

    flash('Recipe successfully added.', category='success')
    return redirect(url_for('views.home'))


@views.route('/delete_recipe')
@login_required
def delete_recipe():

    uuid = request.args.get('recipe_uuid')
    recipe = db.session.query(Recipe).filter(Recipe.uuid == uuid).first()
    db.session.delete(recipe)

    ingredients = db.session.query(Ingredients).filter(Ingredients.uuid == uuid).all()
    for ingredient in ingredients:
        db.session.delete(ingredient)

    db.session.commit()

    return redirect(url_for('views.home'))


@views.route('/view_recipe', methods=['POST', 'GET'])
@login_required
def view_recipe():

    if request.method == 'POST':
        ingredient_list = request.form.getlist('ingredients')
        for ingredient in ingredient_list:
            ingredient = ShoppingList(shopping_item=ingredient)
            db.session.add(ingredient)
            db.session.commit()

    shopping_list = ShoppingList.query.count()

    recipe_uuid = request.args.get('recipe_uuid')
    recipe_id = request.args.get('recipe_uuid')
    recipe = Recipe.query.filter_by(uuid=recipe_id).first()
    ingredients = Ingredients.query.filter_by(uuid=recipe_uuid).all()

    return render_template("view_recipe.html", recipe=recipe, ingredients=ingredients, user=current_user,
                           shopping_list=shopping_list)