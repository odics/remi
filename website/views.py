import json
import shortuuid
from flask import Blueprint, render_template, request, flash, session, redirect, url_for, jsonify
from sqlalchemy import func, desc
from flask_login import login_required, current_user, login_user, logout_user
from recipe_parser import recipe_parser
from .models import Recipe, Ingredients, ShoppingList, Tag, User
from . import db
import re
import os
from werkzeug.security import generate_password_hash, check_password_hash

views = Blueprint('views', __name__)

@views.route('/edit_user/<payload>',methods=['GET', 'POST'])
@login_required
def edit_user(payload):
    ''' Edits an existing user '''

    payload = json.loads(payload)
    user_id = payload["id"]
    new_username = payload["username"]
    new_email = payload["email"]
    is_admin = payload["admin"]

    user_to_edit = User.query.filter_by(id=user_id).first()

    user_to_edit.first_name = new_username
    user_to_edit.email = new_email
    
    if is_admin == "1":
        user_to_edit.admin = True
        
    else:
        user_to_edit.admin = False
        

    db.session.commit()

    return({})


@views.route('/theme/<theme>')
@login_required
def theme(theme):
    '''Changes user appearance theme.'''

    user = User.query.filter_by(id=current_user.id).first()

    if theme == "light":
        user.theme = "1"
        db.session.commit()
        return redirect(url_for('views.settings'))

    
    if theme == "dark":
        user.theme = "2"
        db.session.commit()
        return redirect(url_for('views.settings'))

@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    '''App settings.'''

    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character', category='error')
        elif password1 != password2:
            flash('Passwords must match', category='error')
        elif len(password1) < 7:
            flash('Password must be seven characters or more', category='error')
        else:
            if request.form.get('admin'):
                new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'), admin=True)
                print("user is admin")
                db.session.add(new_user)
                db.session.commit()

                flash('Account created for ' + first_name, category='success')
                return redirect(url_for('views.settings'))
            else:
                new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'), admin=False)
                print("user is NOT admin")
                db.session.add(new_user)
                db.session.commit()

                flash('Account created for ' + first_name, category='success')
                return redirect(url_for('views.settings'))

    # Get a count of all the favorites:
    favorite_total = Recipe.query.filter_by(username=current_user.id, favorite=True).count()

    # Get a count of all the recipes:
    total_recipes = Recipe.query.filter_by(username=current_user.id).count()

    shopping_list = ShoppingList.query.filter_by(username=current_user.id).count()

    user = User.query.filter_by(id=current_user.id).first()
    theme = user.theme

    all_users = User.query.all()

    return render_template("settings.html", favorite_total=favorite_total, total_recipes=total_recipes, shopping_list=shopping_list, user=current_user,
                           all_users=all_users, theme=theme)

@views.route('/delete_user/<user_id>')
@login_required
def delete_user(user_id):
    ''' Deletes a user based on provided user ID '''

    user_to_delete = db.session.query(User).filter_by(id=user_id).first()
    username = user_to_delete.first_name
    db.session.delete(user_to_delete)
    db.session.commit()

    flash("Successfully deleted " + username, category="success")

    return redirect(url_for('views.settings'))

@views.route('/all_recipes', methods=['GET', 'POST'])
@login_required
def all_recipes():
    ''' Lists all available recipes in the database.'''

    shopping_list = ShoppingList.query.filter_by(username=current_user.id).count()
    session['shopping_list'] = shopping_list

    if request.method == 'POST':
        sort_method = request.form.get('sort_method')
        if sort_method == "all":
            page_title = "Showing all recipes"

            recipes = Recipe.query.filter_by(username=current_user.id)
            return render_template("all_recipes.html", user=current_user, recipes=recipes, shopping_list=shopping_list, page_title=page_title)
        else:
            page_title = "Showing all " + sort_method.lower() + " recipes"

            recipes = Recipe.query.filter_by(username=current_user.id, category=sort_method)
            return render_template("all_recipes.html", user=current_user, recipes=recipes, shopping_list=shopping_list, page_title=page_title)

    recipes = Recipe.query.filter_by(username=current_user.id).all()
    page_title = "Showing all recipes"

    # Get a count of all the favorites:
    favorite_total = Recipe.query.filter_by(username=current_user.id, favorite=True).count()

    # Get a count of all the recipes:
    total_recipes = Recipe.query.filter_by(username=current_user.id).count()

    user = User.query.filter_by(id=current_user.id).first()
    theme = user.theme

    return render_template("all_recipes.html", user=current_user, recipes=recipes, shopping_list=shopping_list, 
    page_title=page_title, total_recipes=total_recipes, favorite_total=favorite_total, theme=theme)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    ''' Home page of the website. Lists most recently added recipes. '''

    # Query all of the favorite recipes belonging to currently logged in user:
    # recipes = Recipe.query.filter_by(username=current_user.id, favorite=True).all()

    # Query the last three added recipes:
    recipes = Recipe.query.filter_by(username=current_user.id).order_by(desc(Recipe.id)).limit(3)

    # Get a count of all the favorites:
    favorite_total = Recipe.query.filter_by(username=current_user.id, favorite=True).count()

    # Get a count of all the recipes:
    total_recipes = Recipe.query.filter_by(username=current_user.id).count()

    # Get the most popular category. Start by querying the table:
    category_query = db.session.query(
        Recipe.category, func.count(Recipe.id).label('qty')).group_by(Recipe.category).order_by(desc('qty')).limit(1)
    
    user = User.query.filter_by(id=current_user.id).first()
    theme = user.theme

    # The result is a list containing one tuple of two items. First item (category_query[0][0]) is the name of the popular category.
    # This is wrapped in a try/except block in case the user has no recipes added yet, in which case it will throw an IndexError:
    try:
        popular_category = category_query[0][0]
    except IndexError:
        popular_category = "None"

    shopping_list = ShoppingList.query.filter_by(username=current_user.id).count()
    session['shopping_list'] = shopping_list

    return render_template("home.html", user=current_user, recipes=recipes, shopping_list=shopping_list,
                           favorite_total=favorite_total, total_recipes=total_recipes,
                           popular_category=popular_category, theme=theme)


@views.route('/create_recipe', methods=['GET', 'POST'])
@login_required
def create_recipe():
    ''' Creates a recipe from user-provided information. '''
    if request.method == 'GET':

        # Get a count of all the favorites:
        favorite_total = Recipe.query.filter_by(username=current_user.id, favorite=True).count()

        # Get a count of all the recipes:
        total_recipes = Recipe.query.filter_by(username=current_user.id).count()

        shopping_list = ShoppingList.query.filter_by(username=current_user.id).count()

        session['shopping_list'] = shopping_list

        user = User.query.filter_by(id=current_user.id).first()
        theme = user.theme
        
        return render_template("create_recipe.html", user=current_user, shopping_list=shopping_list, total_recipes=total_recipes, 
                               favorite_total=favorite_total, theme=theme)
    
    if request.method == 'POST':
        prep_time = request.form.get('prep_time')
        total_time = request.form.get('total_time')
        cook_time = request.form.get('cook_time')
        servings = request.form.get('servings')
        recipe_category = request.form.get('recipe_category')
        recipe_title = request.form.get('recipe_title')

        ingredient_list = request.form.getlist('ingredients')
        ingredient_type = request.form.getlist('ing_type')
        instructions = request.form.getlist('instructions')
        tags = request.form.getlist('custom_recipe_tags')

        instructions_json = {}

        for i in range(len(instructions)):
            instructions_json[i] = instructions[i]

        instructions_json = json.dumps(instructions_json)

        uuid = shortuuid.uuid()

        for i in range(0, len(ingredient_list)):
            if ingredient_type[i] == "misc":
                    ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="misc", ing_display="Misc.")
                    db.session.add(ingredient)
                    db.session.commit()

            if ingredient_type[i] == "produce":
                    ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="produce", ing_display="Produce")
                    db.session.add(ingredient)
                    db.session.commit()

            if ingredient_type[i] == "meat":
                    ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="meat", ing_display="Meat")
                    db.session.add(ingredient)
                    db.session.commit()

            if ingredient_type[i] == "coffee_tea":
                    ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="coffee_tea", ing_display="Coffee and Tea")
                    db.session.add(ingredient)
                    db.session.commit()

            if ingredient_type[i] == "pasta":
                    ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="pasta", ing_display="Pasta")
                    db.session.add(ingredient)
                    db.session.commit()

            if ingredient_type[i] == "frozen":
                    ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="frozen", ing_display="Frozen Food")
                    db.session.add(ingredient)
                    db.session.commit()

            if ingredient_type[i] == "dairy_bread":
                    ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="dairy_bread", ing_display="Dairy and Bread")
                    db.session.add(ingredient)
                    db.session.commit()

            if ingredient_type[i] == "7":
                    pass
        
        if recipe_category == "0":
            recipe_category = "Breakfast"
        elif recipe_category == "1":
            recipe_category = "Lunch"
        elif recipe_category == "2":
            recipe_category = "Dinner"
        elif recipe_category == "3":
            recipe_category = "Dessert"
        elif recipe_category == "4":
            recipe_category = "Sides"

        new_recipe = Recipe(username=current_user.id, prep_time=prep_time, cook_time=cook_time, 
                            recipe_name=recipe_title, total_time=total_time, servings=servings,category=recipe_category, 
                            uuid=uuid, favorite=False, instructions_json=instructions_json, image="custom_recipe.png")

        for tag in tags:
            new_tag = Tag(tag_name=str(tag).upper())
            new_recipe.tags.append(new_tag)

            db.session.add(new_tag)
            db.session.commit()

        db.session.add(new_recipe)
        db.session.commit()

        flash('Recipe successfully created.', category='success')
        return redirect(url_for('views.home'))


@views.route('/search/<query>', methods=['GET', 'POST'])
@login_required
def search_recipes(query):
    ''' Allows for searching for a recipe based on recipe title. '''

    shopping_list = session.get('shopping_list', None)
    search_query = "%" + query + "%"

    search_results = Recipe.query.filter(Recipe.recipe_name.like(search_query), Recipe.username==current_user.id).all()
    search_count = Recipe.query.filter(Recipe.recipe_name.like(search_query), Recipe.username==current_user.id).count()

    return(render_template("search_results.html", user=current_user, query=query, results=search_results, 
        count=search_count, shopping_list=shopping_list))


@views.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    ''' Import and preview a recipe before saving to database. '''
    shopping_list = session.get('shopping_list', None)

      # Get a count of all the favorites:
    favorite_total = Recipe.query.filter_by(username=current_user.id, favorite=True).count()

    # Get a count of all the recipes:
    total_recipes = Recipe.query.filter_by(username=current_user.id).count()

    user = User.query.filter_by(id=current_user.id).first()
    theme = user.theme

    if request.method == 'POST':
        url = request.form.get('recipe_url')

        recipe = recipe_parser(url)

        if recipe == 1:
            return "Error 1"
        else:
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
            session['original_url'] = recipe.original_url
            session['date_parsed'] = recipe.date_parsed
            session['instructions_json'] = recipe.instructions_json
            shopping_list = session.get('shopping_list', None)

            return render_template("preview_recipe.html", user=current_user, title=recipe.title, prep=recipe.prep,
                                   cook=recipe.cook,
                                   rest=recipe.rest, total=recipe.total, servings=recipe.servings,
                                   ingredients=recipe.ingredients, instructions=recipe.instructions, image=recipe.image,
                                   ingredient_list=recipe.ingredient_list, shopping_list=shopping_list,
                                   original_url=recipe.original_url, date_parsed=recipe.date_parsed, 
                                   instructions_json=json.loads(recipe.instructions_json))

    return render_template("add_recipe.html", user=current_user, shopping_list=shopping_list, total_recipes=total_recipes,
                           favorite_total=favorite_total, theme=theme)


@views.route('/save_recipe', methods=['GET', 'POST'])
@login_required
def save_recipe_to_db():
    ''' Save a recipe after importing from URL. '''

    user_id = session.get('user_id', None)
    title = request.form.get('recipe_title')
    prep = request.form.get('prep_time')
    cook = request.form.get('cook_time')
    rest = session.get('rest', None)
    total = request.form.get('total_time')
    servings = request.form.get('servings')
    instructions = session.get('instructions', None)
    image = session.get('image', None)
    ingredient_list = session.get('ingredient_list', None)
    ingredients = session.get('ingredients', None)
    uuid = shortuuid.uuid()
    original_url = session.get('original_url', None)
    date_parsed = session.get('date_parsed', None)
    instructions_json = session.get('instructions_json', None)

    if request.method == 'POST':

        category = request.form.get('recipe_category')
        ingredient_list = request.form.getlist('ingredient_list')
        ingredient_type = request.form.getlist('ing_type')

        if category == "0":
            recipe_category = "Breakfast"
        elif category == "1":
            recipe_category = "Lunch"
        elif category == "2":
            recipe_category = "Dinner"
        elif category == "3":
            recipe_category = "Dessert"
        elif category == "4":
            recipe_category = "Sides"
        else:
            recipe_category = "None"

        for i in range(0, len(ingredient_list)):
            if ingredient_type[i] == "misc":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="misc", ing_display="Misc.")
                db.session.add(ingredient)
                db.session.commit()

            if ingredient_type[i] == "produce":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="produce", ing_display="Produce")
                db.session.add(ingredient)
                db.session.commit()

            if ingredient_type[i] == "meat":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="meat", ing_display="Meat")
                db.session.add(ingredient)
                db.session.commit()

            if ingredient_type[i] == "coffee_tea":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="coffee_tea", ing_display="Coffee and Tea")
                db.session.add(ingredient)
                db.session.commit()

            if ingredient_type[i] == "pasta":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="pasta", ing_display="Pasta")
                db.session.add(ingredient)
                db.session.commit()

            if ingredient_type[i] == "frozen":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="frozen", ing_display="Frozen Food")
                db.session.add(ingredient)
                db.session.commit()

            if ingredient_type[i] == "dairy_bread":
                ingredient = Ingredients(uuid=uuid, ingredient=ingredient_list[i], ing_type="dairy_bread", ing_display="Dairy and Bread")
                db.session.add(ingredient)
                db.session.commit()

            if ingredient_type[i] == "7":
                pass

    new_recipe = Recipe(username=user_id, prep_time=prep, cook_time=cook, ingredients=ingredients,
                        instructions=instructions, recipe_name=title, image=image, total_time=total, servings=servings,
                        uuid=uuid, original_url=original_url, date_parsed=date_parsed, favorite=False,
                        category=recipe_category, instructions_json=instructions_json)

    tags = request.form.getlist('new_tag')

    for tag in tags:
        new_tag = Tag(tag_name=str(tag))
        new_recipe.tags.append(new_tag)

        db.session.add(new_tag)
        db.session.commit()

    db.session.add(new_recipe)
    db.session.commit()

    flash('Recipe successfully added.', category='success')
    return redirect(url_for('views.home'))


@views.route('/delete_recipe', methods=['GET', 'POST'])
@login_required
def delete_recipe():
    ''' Delete a recipe and remain on current page. '''
    recipe_uuid = json.loads(request.data)
    recipe_uuid = recipe_uuid.get('recipe_id')

    recipe = db.session.query(Recipe).filter(Recipe.uuid == recipe_uuid).first()

    # if recipe.image != "custom_recipe.png":
    #     image_file_name = "./website/static/" + recipe.image
    #     os.remove(image_file_name)

    db.session.delete(recipe)

    ingredients = db.session.query(Ingredients).filter(Ingredients.uuid == recipe_uuid).all()
    for ingredient in ingredients:
        db.session.delete(ingredient)

    db.session.commit()

    return jsonify({})


@views.route('/delete_recipe_go_home/<recipe_id>', methods=['GET', 'POST'])
@login_required
def delete_recipe_go_home(recipe_id):
    ''' Delete a recipe and go to the home page after doing so. '''
    recipe_uuid = recipe_id
  
    recipe = db.session.query(Recipe).filter(Recipe.uuid == recipe_uuid).first()

    # if recipe.image != "custom_recipe.png":
    #     image_file_name = "./website/static/" + recipe.image
    #     os.remove(image_file_name)

    db.session.delete(recipe)

    ingredients = db.session.query(Ingredients).filter(Ingredients.uuid == recipe_uuid).all()
    for ingredient in ingredients:
        db.session.delete(ingredient)

    db.session.commit()

    flash("Successfully deleted " + recipe.recipe_name + ".", category='success')
    
    return redirect(url_for('views.home'))


@views.route('/favorites', methods=['GET'])
@login_required
def show_favorites():
    ''' Show all favorite recipes. '''
    shopping_list = ShoppingList.query.filter_by(username=current_user.id).count()
    fav_recipe = Recipe.query.filter_by(username=current_user.id, favorite=True).all()

    # Get a count of all the favorites:
    favorite_total = Recipe.query.filter_by(username=current_user.id, favorite=True).count()

    # Get a count of all the recipes:
    total_recipes = Recipe.query.filter_by(username=current_user.id).count()

    user = User.query.filter_by(id=current_user.id).first()
    theme = user.theme

    return render_template("favorite_recipes.html", recipes=fav_recipe, user=current_user, shopping_list=shopping_list,
    favorite_total=favorite_total, total_recipes=total_recipes, theme=theme)


@views.route('/random_recipe', methods=['POST', 'GET'])
@login_required
def random_recipe():
    ''' Pull a random recipe from the database. '''

    if request.method == 'POST':
        category = request.form.getlist('category')
        ingredient_list = request.form.getlist('ingredients')
        for ingredient in ingredient_list:
            ingredient = ShoppingList(shopping_item=ingredient, category=category[ingredient_list.index(ingredient)], username=current_user.id)
            db.session.add(ingredient)
            db.session.commit()

    shopping_list = ShoppingList.query.filter_by(username=current_user.id).count()

    recipe = Recipe.query.filter_by(username=current_user.id).group_by(func.random()).first()
    ingredients = Ingredients.query.filter_by(uuid=recipe.uuid).all()
    instructions_json = json.loads(recipe.instructions_json)
    
    user = User.query.filter_by(id=current_user.id).first()
    theme = user.theme

    return render_template("view_recipe.html", recipe=recipe, ingredients=ingredients, user=current_user,
                           shopping_list=shopping_list, view_id=recipe.uuid, instructions_json=instructions_json, theme=theme)


@views.route('/view_recipe/<recipe_uuid>', methods=['POST', 'GET'])
@login_required
def view_recipe(recipe_uuid):
    ''' View a specific recipe in detail. '''

     # Get a count of all the favorites:
    favorite_total = Recipe.query.filter_by(username=current_user.id, favorite=True).count()

        # Get a count of all the recipes:
    total_recipes = Recipe.query.filter_by(username=current_user.id).count()

    user = User.query.filter_by(id=current_user.id).first()
    theme = user.theme

    if request.method == 'POST':
        category = request.form.getlist('category')
        ingredient_list = request.form.getlist('ingredients')
        for ingredient in ingredient_list:
            ingredient = ShoppingList(shopping_item=ingredient, category=category[ingredient_list.index(ingredient)], username=current_user.id)
            db.session.add(ingredient)
            db.session.commit()

        flash('Success fully added ingredients to shopping list', category="success")

    shopping_list = ShoppingList.query.filter_by(username=current_user.id).count()

    recipe_id = recipe_uuid
    recipe = Recipe.query.filter_by(uuid=recipe_id).first()
    ingredients = Ingredients.query.filter_by(uuid=recipe_uuid).all()
    instructions_json = json.loads(recipe.instructions_json)

    return render_template("view_recipe.html", recipe=recipe, ingredients=ingredients, user=current_user,
                           shopping_list=shopping_list, view_id=recipe_id, instructions_json=instructions_json, 
                           favorite_total=favorite_total, total_recipes=total_recipes, theme=theme)


@views.route('/edit_recipe/<recipe_uuid>', methods=['POST', 'GET'])
@login_required
def edit_recipe(recipe_uuid):
    ''' Edits and updates an existing recipe. '''

     # Get a count of all the favorites:
    favorite_total = Recipe.query.filter_by(username=current_user.id, favorite=True).count()

    # Get a count of all the recipes:
    total_recipes = Recipe.query.filter_by(username=current_user.id).count()

    user = User.query.filter_by(id=current_user.id).first()
    theme = user.theme

    if request.method == 'POST':

        tags = request.form.getlist('new_tag')
        recipe_title = request.form.get('recipe_title')
        recipe_id = request.form.get('recipe_id')

        ing_type = request.form.getlist('ing_type')
        ingredient_to_update = request.form.getlist('ingredient_list')
        ingredient_id = request.form.getlist('ingredient_id')

        instructions_to_update = request.form.getlist('instructions')

        recipe_prep_time = request.form.get('prep_time')
        recipe_cook_time = request.form.get('cook_time')
        recipe_total_time = request.form.get('total_time')
        recipe_servings = request.form.get('servings')
        recipe_category = request.form.get('recipe_category')

        if recipe_category == "0":
            recipe_category = "Breakfast"
        elif recipe_category == "1":
            recipe_category = "Lunch"
        elif recipe_category == "2":
            recipe_category = "Dinner"
        elif recipe_category == "3":
            recipe_category = "Dessert"
        elif recipe_category == "4":
            recipe_category = "Sides"
        else:
            recipe_category = "None"

        for i in range(0, len(ingredient_to_update)):
            ingredient_update = Ingredients.query.filter_by(id=ingredient_id[i]).first()
            ingredient_update.ingredient = ingredient_to_update[i]

            if ing_type[i] == "misc":
                ingredient_update.ing_type = ing_type[i]
                ingredient_update.ing_display = "Misc."

            elif ing_type[i] == "produce":
                ingredient_update.ing_type = ing_type[i]
                ingredient_update.ing_display = "Produce"

            elif ing_type[i] == "meat":
                ingredient_update.ing_type = ing_type[i]
                ingredient_update.ing_display = "Meat"

            elif ing_type[i] == "coffee_tea":
                ingredient_update.ing_type = ing_type[i]
                ingredient_update.ing_display = "Coffee and Tea"

            elif ing_type[i] == "pasta":
                ingredient_update.ing_type = ing_type[i]
                ingredient_update.ing_display = "Pasta"

            elif ing_type[i] == "frozen":
                ingredient_update.ing_type = ing_type[i]
                ingredient_update.ing_display = "Frozen Food"

            elif ing_type[i] == "dairy_bread":
                ingredient_update.ing_type = ing_type[i]
                ingredient_update.ing_display = "Dairy"

            db.session.commit()

        instructions_json = {}
        for i in range(0, len(instructions_to_update)):
            instructions_json[i] = instructions_to_update[i]

        instructions_json = json.dumps(instructions_json)

        recipe_update = Recipe.query.filter_by(id=recipe_id).first()
        recipe_update.instructions_json = instructions_json
        recipe_update.recipe_name = recipe_title
        recipe_update.prep_time = recipe_prep_time
        recipe_update.cook_time = recipe_cook_time
        recipe_update.total_time = recipe_total_time
        recipe_update.servings = recipe_servings
        recipe_update.category = recipe_category
        
        if tags:
            for tag in tags:
                new_tag = Tag(tag_name=str(tag))
                recipe_update.tags.append(new_tag)

                db.session.add(new_tag)

        db.session.commit()

        return redirect(url_for('views.view_recipe', recipe_uuid=recipe_uuid, theme=theme))

    shopping_list = ShoppingList.query.filter_by(username=current_user.id).count()

    recipe_id = recipe_uuid
    recipe = Recipe.query.filter_by(uuid=recipe_id).first()
    instructions_json = json.loads(recipe.instructions_json)
    ingredients = Ingredients.query.filter_by(uuid=recipe_uuid).all()

    return render_template("edit_recipe.html", recipe=recipe, ingredients=ingredients, user=current_user,
                           shopping_list=shopping_list, view_id=recipe_id, instructions_json=instructions_json, 
                           total_recipes=total_recipes, favorite_total=favorite_total, theme=theme)


@views.route('/delete_tag', methods=['POST'])
@login_required
def delete_tag():
    ''' Deletes a specific recipe's tag. '''

    tag = json.loads(request.data)

    tag_id = tag['tag_id']

    recipe_id = tag['recipe_id']

    tag_to_delete = Tag.query.get(tag_id)

    recipe_to_remove_tag_from = Recipe.query.filter_by(id=recipe_id).first()

    recipe_to_remove_tag_from.tags.remove(tag_to_delete)
    db.session.commit()

    return jsonify({})

@views.route('/show_tags')
@login_required
def show_tags():

    # Get a count of all the favorites:
    favorite_total = Recipe.query.filter_by(username=current_user.id, favorite=True).count()

    # Get a count of all the recipes:
    total_recipes = Recipe.query.filter_by(username=current_user.id).count()

    shopping_list = ShoppingList.query.filter_by(username=current_user.id).count()

    user = User.query.filter_by(id=current_user.id).first()
    theme = user.theme
    
    return render_template("show_tags.html", total_recipes=total_recipes ,favorite_total=favorite_total, shopping_list=shopping_list, theme=theme)

@views.route('/fetch_tags/<match_tag>', methods=['POST', 'GET'])
@login_required
def fetch_tags(match_tag):
    '''Takes in a string and performes a regex match based on starting characters. Returns a JSON object of matched tags.'''
    if match_tag:
        recipes = Recipe.query.filter_by(username=current_user.id)

        tag_list = []

        for recipe in recipes:
            if recipe.tags:
                for tag in recipe.tags:
                    tag_list.append(tag)

        stripped_tags = []

        for tag in tag_list:
            if tag.tag_name not in stripped_tags:
                stripped_tags.append(tag.tag_name)
        
        filtered_tags = []
        regex = "^" + match_tag
       
        for tag_result in stripped_tags:
            if re.match(regex, tag_result, re.IGNORECASE):
                filtered_tags.append({"tag_name": tag_result})

        

        for tag in filtered_tags:
            count = 0
            recipes = Recipe.query.filter_by(username=current_user.id).all()
            for recipe in recipes:
                for recipe_tag in recipe.tags:
                    if recipe_tag.tag_name == tag["tag_name"]:
                        count = count + 1
            tag["count"] = count
            print(tag)

        return(json.dumps(filtered_tags))
    else:
        return({""})
    
@views.route('/fetch_tagged_recipe/<tag_query>')
@login_required
def fetch_tagged_recipe(tag_query):

    # Get a count of all the favorites:
    favorite_total = Recipe.query.filter_by(username=current_user.id, favorite=True).count()

    # Get a count of all the recipes:
    total_recipes = Recipe.query.filter_by(username=current_user.id).count()

    shopping_list = ShoppingList.query.filter_by(username=current_user.id).count()

    recipes = Recipe.query.filter_by(username=current_user.id).all()

    recipe_list = []

    for recipe in recipes:
        for tag in recipe.tags:
            if tag.tag_name == tag_query:
                recipe_list.append(recipe)

    user = User.query.filter_by(id=current_user.id).first()
    theme = user.theme

    return render_template("fetch_tagged_recipes.html", favorite_total=favorite_total, total_recipes=total_recipes,
                           shopping_list=shopping_list, recipes=recipe_list, tag=tag_query, theme=theme)


@views.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    ''' Adds a recipe to the favorite list. '''

    recipe = json.loads(request.data)
    recipe_id = recipe['recipe_id']

    recipe = Recipe.query.get(recipe_id)
    recipe.favorite = True

    db.session.commit()

    return jsonify({})


@views.route('/remove_favorite', methods=['POST'])
@login_required
def remove_favorite():
    ''' Removes a recipe from the favorite list. '''

    recipe = json.loads(request.data)
    recipe_id = recipe['recipe_id']

    recipe = Recipe.query.get(recipe_id)
    recipe.favorite = False

    db.session.commit()

    return jsonify({})


@views.route('/cart', methods=['POST', 'GET'])
@login_required
def cart():
    ''' Shows current shopping cart. '''
    
     # Get a count of all the favorites:
    favorite_total = Recipe.query.filter_by(username=current_user.id, favorite=True).count()

    # Get a count of all the recipes:
    total_recipes = Recipe.query.filter_by(username=current_user.id).count()

    user = User.query.filter_by(id=current_user.id).first()
    theme = user.theme

    if request.method == 'POST':
        category = request.form.get('ing_type')
        ingredient = request.form.get('ingredient')

        ingredient_to_add = ShoppingList(shopping_item=ingredient, category=category, username=current_user.id)
        db.session.add(ingredient_to_add)
        db.session.commit()

        return redirect(url_for('views.cart'))

    shopping_list = ShoppingList.query.filter_by(username=current_user.id).count()
    shopping_items_pasta = ShoppingList.query.filter_by(username=current_user.id, category='pasta').all()
    shopping_items_produce = ShoppingList.query.filter_by(username=current_user.id, category='produce').all()
    shopping_items_misc = ShoppingList.query.filter_by(username=current_user.id, category='misc').all()
    shopping_items_dairy = ShoppingList.query.filter_by(username=current_user.id, category='dairy_bread').all()
    shopping_items_meat = ShoppingList.query.filter_by(username=current_user.id, category='meat').all()
    shopping_items_frozen = ShoppingList.query.filter_by(username=current_user.id, category='frozen').all()
    shopping_items_coffee = ShoppingList.query.filter_by(username=current_user.id, category='coffee_tea').all()

    pasta_to_copy = ""
    produce_to_copy = ""
    misc_to_copy = ""
    dairy_to_copy = ""
    meat_to_copy = ""
    frozen_to_copy = ""
    coffee_to_copy = ""

    if shopping_items_pasta:
        for item in shopping_items_pasta:
            pasta_to_copy = pasta_to_copy + "- " + item.shopping_item + "\n"
    elif shopping_items_produce:
        for item in shopping_items_produce:
            produce_to_copy = produce_to_copy + "- " + item.shopping_item + "\n"
    elif shopping_items_misc:
        for item in shopping_items_misc:
            misc_to_copy = misc_to_copy + "- " + item.shopping_item + "\n"
    elif shopping_items_dairy:
        for item in shopping_items_dairy:
            dairy_to_copy = dairy_to_copy + "- " + item.shopping_item + "\n"
    elif shopping_items_meat:
        for item in shopping_items_meat:
            meat_to_copy = meat_to_copy + "- " + item.shopping_item + "\n"
    elif shopping_items_frozen:
        for item in shopping_items_frozen:
            frozen_to_copy = frozen_to_copy + "- " + item.shopping_item + "\n"
    elif shopping_items_coffee:
        for item in shopping_items_coffee:
            coffee_to_copy = coffee_to_copy + "- " + item.shopping_item + "\n"

    return render_template("cart.html", user=current_user, shopping_list=shopping_list, pasta=shopping_items_pasta,
                           produce=shopping_items_produce, misc=shopping_items_misc, dairy=shopping_items_dairy,
                           meat=shopping_items_meat, frozen=shopping_items_frozen, coffee=shopping_items_coffee,
                           pasta_to_copy=pasta_to_copy, produce_to_copy=produce_to_copy,misc_to_copy=misc_to_copy,
                           dairy_to_copy=dairy_to_copy, meat_to_copy=meat_to_copy, frozen_to_copy=frozen_to_copy,
                           coffee_to_copy=coffee_to_copy, favorite_total=favorite_total, total_recipes=total_recipes, theme=theme)


@views.route('/delete_item', methods=['POST'])
@login_required
def delete_item():
    ''' Remove an item from the shopping list/cart. '''

    item = json.loads(request.data)
    item_id = item['item_id']
    item_to_delete = ShoppingList.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()

    return jsonify({})


@views.route('/clear_cart', methods=['POST'])
@login_required
def clear_cart():
    ''' Clears all items from the shopping list/cart. '''

    db.session.query(ShoppingList).delete()
    db.session.commit()

    return jsonify({})

@views.route('/update_cart/<item_id>/<updated_value>', methods=['GET'])
@login_required
def update_car(item_id, updated_value):
    ''' Dynamically updates given cart item. '''

    item_to_update = ShoppingList.query.filter_by(username=current_user.id, id=item_id).first()
    print(item_to_update.shopping_item)
    print(updated_value)
    item_to_update.shopping_item = updated_value
    db.session.commit()

    return jsonify({})