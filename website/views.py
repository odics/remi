from flask import Blueprint, render_template, request, flash, session, redirect, url_for, jsonify
from flask_login import login_required, current_user
import json
from .models import Recipe, Ingredients, ShoppingList
from recipe_parser import recipe_parser
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
    shopping_list = session.get('shopping_list', None)

    if request.method == 'POST':
        url = request.form.get('recipe_url')

        recipe = recipe_parser(url)

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
        shopping_list = session.get('shopping_list', None)

        return render_template("list_recipe.html", user=current_user, title=recipe.title, prep=recipe.prep,
                               cook=recipe.cook,
                               rest=recipe.rest, total=recipe.total, servings=recipe.servings,
                               ingredients=recipe.ingredients, instructions=recipe.instructions, image=recipe.image,
                               ingredient_list=recipe.ingredient_list, shopping_list=shopping_list)

    return render_template("add_recipe.html", user=current_user, shopping_list=shopping_list)


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

    if request.method == 'POST':
        for ingredient in ingredient_list:
            form_id = request.form[str(ingredient_list.index(ingredient))]
            if form_id == "0":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient, ing_type="misc")
                db.session.add(ingredient)
                db.session.commit()

            if form_id == "1":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient, ing_type="produce")
                db.session.add(ingredient)
                db.session.commit()

            if form_id == "2":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient, ing_type="meat")
                db.session.add(ingredient)
                db.session.commit()

            if form_id == "3":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient, ing_type="coffee_tea")
                db.session.add(ingredient)
                db.session.commit()

            if form_id == "4":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient, ing_type="pasta")
                db.session.add(ingredient)
                db.session.commit()

            if form_id == "5":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient, ing_type="frozen")
                db.session.add(ingredient)
                db.session.commit()

            if form_id == "6":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient, ing_type="dairy_bread")
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
        category = request.form.getlist('category')
        ingredient_list = request.form.getlist('ingredients')
        for ingredient in ingredient_list:
            ingredient = ShoppingList(shopping_item=ingredient, category=category[ingredient_list.index(ingredient)])
            db.session.add(ingredient)
            db.session.commit()

    shopping_list = ShoppingList.query.count()

    recipe_uuid = request.args.get('recipe_uuid')
    recipe_id = request.args.get('recipe_uuid')
    recipe = Recipe.query.filter_by(uuid=recipe_id).first()
    ingredients = Ingredients.query.filter_by(uuid=recipe_uuid).all()

    return render_template("view_recipe.html", recipe=recipe, ingredients=ingredients, user=current_user,
                           shopping_list=shopping_list)


@views.route('/cart')
@login_required
def cart():
    shopping_list = ShoppingList.query.count()
    shopping_items_pasta = ShoppingList.query.filter_by(category='pasta').all()
    shopping_items_produce = ShoppingList.query.filter_by(category='produce').all()
    shopping_items_misc = ShoppingList.query.filter_by(category='misc').all()
    shopping_items_dairy = ShoppingList.query.filter_by(category='dairy_bread').all()
    shopping_items_meat = ShoppingList.query.filter_by(category='meat').all()
    shopping_items_frozen = ShoppingList.query.filter_by(category='frozen').all()
    shopping_items_coffee = ShoppingList.query.filter_by(category='coffee_tea').all()

    return render_template("cart.html", user=current_user, shopping_list=shopping_list, pasta=shopping_items_pasta,
                           produce=shopping_items_produce, misc=shopping_items_misc, dairy=shopping_items_dairy,
                           meat=shopping_items_meat, frozen=shopping_items_frozen, coffee=shopping_items_coffee)


@views.route('/delete_item', methods=['POST'])
@login_required
def delete_item():
    item = json.loads(request.data)
    item_id = item['item_id']
    item_to_delete = ShoppingList.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()

    return jsonify({})


@views.route('/clear_cart', methods=['POST'])
@login_required
def clear_cart():
    db.session.query(ShoppingList).delete()
    db.session.commit()

    return jsonify({})

