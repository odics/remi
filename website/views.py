from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from .models import Recipe
from all_recipes_parser import allrecipes_parse


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

    return render_template("home.html", user=current_user)


@views.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    if request.method == 'POST':
        url = request.form.get('recipe_url')

        recipe = allrecipes_parse(url)

    print(recipe.prep)
    return render_template("add_recipe.html", user=current_user)
