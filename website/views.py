from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from flask_login import login_required, current_user
import json
from .models import Recipe
from all_recipes_parser import allrecipes_parse
from . import db

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
    return render_template("home.html", user=current_user, recipes=recipes)


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

    new_recipe = Recipe(username=user_id, prep_time=prep, cook_time=cook, ingredients=ingredients,
                        instructions=instructions, recipe_name=title, image=image)

    db.session.add(new_recipe)
    db.session.commit()

    flash('Recipe successfully added.', category='success')
    return redirect(url_for('views.home'))


@views.route('/delete_recipe')
@login_required
def delete_recipe():

    recipe_id = request.args.get('recipe_id')
    recipe = db.session.query(Recipe).filter(Recipe.id == recipe_id).first()
    db.session.delete(recipe)
    db.session.commit()

    return redirect(url_for('views.home'))


@views.route('/view_recipe')
@login_required
def view_recipe():

    recipe_id = request.args.get('recipe_id')
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    return render_template("view_recipe.html", recipe=recipe, user=current_user)
