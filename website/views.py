import json
import shortuuid
from flask import Blueprint, render_template, request, flash, session, redirect, url_for, jsonify
from sqlalchemy import func, desc
from flask_login import login_required, current_user
from recipe_parser import recipe_parser
from .models import Recipe, Ingredients, ShoppingList, Tag
from . import db
import os

views = Blueprint('views', __name__)

@views.route('/all_recipes', methods=['GET', 'POST'])
@login_required
def all_recipes():
    ''' Lists all available recipes in the database.'''

    shopping_list = ShoppingList.query.count()
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
    return render_template("all_recipes.html", user=current_user, recipes=recipes, shopping_list=shopping_list, page_title=page_title)


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

    # The result is a list containing one tuple of two items. First item (category_query[0][0]) is the name of the popular category.
    # This is wrapped in a try/except block in case the user has no recipes added yet, in which case it will throw an IndexError:
    try:
        popular_category = category_query[0][0]
    except IndexError:
        popular_category = "None"

    shopping_list = ShoppingList.query.count()
    session['shopping_list'] = shopping_list

    return render_template("home.html", user=current_user, recipes=recipes, shopping_list=shopping_list,
                           favorite_total=favorite_total, total_recipes=total_recipes,
                           popular_category=popular_category)


@views.route('/create_recipe', methods=['GET', 'POST'])
@login_required
def create_recipe():
    ''' Creates a recipe from user-provided information. '''

    prep_time = request.form.get('prep_time')
    total_time = request.form.get('total_time')
    cook_time = request.form.get('cook_time')
    servings = request.form.get('servings')
    recipe_category = request.form.get('recipe_category')
    recipe_title = request.form.get('recipe_title')

    ingredient_list = request.form.getlist('ingredients')
    ingredient_type = request.form.getlist('ing_type')
    instructions = request.form.getlist('instructions')

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

    new_recipe = Recipe(username=current_user.id, prep_time=prep_time, cook_time=cook_time, 
                        recipe_name=recipe_title, total_time=total_time, servings=servings,category=recipe_category, 
                        uuid=uuid, favorite=False, instructions_json=instructions_json, image="placeholder.jpg")

    db.session.add(new_recipe)
    db.session.commit()

    flash('Recipe successfully created.', category='success')
    return redirect(url_for('views.home'))


@views.route('/search', methods=['GET', 'POST'])
@login_required
def search_recipes():
    ''' Allows for searching for a recipe based on recipe title and category. '''

    shopping_list = session.get('shopping_list', None)

    if request.form.get('search_query'):
        search_query = "%" + request.form.get('search_query') + "%"
        query_for_title = request.form.get('search_query')
        session['session_title'] = query_for_title
        session['session_query'] = search_query

    elif session.get('session_query', None):
        search_query = session.get('session_query', None)
        query_for_title = session.get('session_title')

    else:
        category = request.form.get('sort_method')

        if category == "all":
            search_results = Recipe.query.filter_by(username=current_user.id).all()
            search_count = Recipe.query.filter_by(username=current_user.id).count()

            query_for_title = "all categories"

            return(render_template("search_results.html", user=current_user, query=query_for_title, results=search_results,
            count=search_count, shopping_list=shopping_list))
        else:
            search_results = Recipe.query.filter_by(username=current_user.id, category=category).all()
            search_count = Recipe.query.filter_by(username=current_user.id, category=category).count()

            return(render_template("search_results.html", user=current_user, query=query_for_title, results=search_results,
            count=search_count, shopping_list=shopping_list))

    if request.form.get('sort_method'):
        category = request.form.get('sort_method')
        print(category)
        if category == "all":
            search_query = session.get('session_query', None)
            query_for_title = session.get('session_title', None)

            search_results = Recipe.query.filter(Recipe.recipe_name.like(search_query), Recipe.username==current_user.id).all()
            search_count = Recipe.query.filter(Recipe.recipe_name.like(search_query), Recipe.username==current_user.id).count()

            session.pop('session_query', None)
            return(render_template("search_results.html", user=current_user, query=query_for_title, results=search_results, 
            count=search_count, shopping_list=shopping_list))
        
        else:
            search_query = session.get('session_query', None)
            query_for_title = session.get('session_title', None)
            print(search_query)

            search_results = Recipe.query.filter(Recipe.recipe_name.like(search_query), 
            Recipe.username==current_user.id).filter_by(username=current_user.id, category=category).all()
            search_count = Recipe.query.filter(Recipe.recipe_name.like(search_query), Recipe.username==current_user.id).count()
            
            session.pop('session_query', None)
            return(render_template("search_results.html", user=current_user, query=query_for_title, results=search_results, 
            count=search_count, shopping_list=shopping_list))
            
    else:
        search_results = Recipe.query.filter(Recipe.recipe_name.like(search_query)).all()
        search_count = Recipe.query.filter(Recipe.recipe_name.like(search_query)).count()

        session.pop('session_query', None)
        return(render_template("search_results.html", user=current_user, query=query_for_title, results=search_results, 
        count=search_count, shopping_list=shopping_list))


@views.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    ''' Import and preview a recipe before saving to database. '''
    shopping_list = session.get('shopping_list', None)

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

    return render_template("add_recipe.html", user=current_user, shopping_list=shopping_list)


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

    tags = request.form.getlist('recipe_tags')

    for tag in tags:
        new_tag = Tag(tag_name=str(tag).upper())
        new_recipe.tags.append(new_tag)

        db.session.add(new_tag)
        db.session.commit()

    db.session.add(new_recipe)
    db.session.commit()

    flash('Recipe successfully added.', category='success')
    return redirect(url_for('views.home'))


@views.route('/delete_recipe', methods=['POST'])
@login_required
def delete_recipe():
    ''' Delete a recipe and remain on current page. '''
    recipe_uuid = json.loads(request.data)
    recipe_uuid = recipe_uuid.get('recipe_id')

    recipe = db.session.query(Recipe).filter(Recipe.uuid == recipe_uuid).first()
    image_file_name = "./website/static/" + recipe.image
    os.remove(image_file_name)

    db.session.delete(recipe)

    ingredients = db.session.query(Ingredients).filter(Ingredients.uuid == recipe_uuid).all()
    for ingredient in ingredients:
        db.session.delete(ingredient)

    db.session.commit()

    return jsonify({})


@views.route('/delete_recipe_go_home', methods=['POST'])
@login_required
def delete_recipe_go_home():
    ''' Delete a recipe and go to the home page after doing so. '''
    recipe_uuid = json.loads(request.data)
    recipe_uuid = recipe_uuid.get('recipe_id')

    recipe = db.session.query(Recipe).filter(Recipe.uuid == recipe_uuid).first()

    image_file_name = "./website/static/" + recipe.image
    os.remove(image_file_name)

    db.session.delete(recipe)

    ingredients = db.session.query(Ingredients).filter(Ingredients.uuid == recipe_uuid).all()
    for ingredient in ingredients:
        db.session.delete(ingredient)

    db.session.commit()

    return redirect(url_for('views.home'))


@views.route('/favorites', methods=['GET'])
@login_required
def show_favorites():
    ''' Show all favorite recipes. '''
    shopping_list = ShoppingList.query.count()
    fav_recipe = Recipe.query.filter_by(username=current_user.id, favorite=True).all()
    print(fav_recipe)

    return render_template("favorite_recipes.html", recipes=fav_recipe, user=current_user, shopping_list=shopping_list)


@views.route('/random_recipe', methods=['POST', 'GET'])
@login_required
def random_recipe():
    ''' Pull a random recipe from the database. '''

    if request.method == 'POST':
        category = request.form.getlist('category')
        ingredient_list = request.form.getlist('ingredients')
        for ingredient in ingredient_list:
            ingredient = ShoppingList(shopping_item=ingredient, category=category[ingredient_list.index(ingredient)])
            db.session.add(ingredient)
            db.session.commit()

    shopping_list = ShoppingList.query.count()

    recipe = Recipe.query.filter_by(username=current_user.id).group_by(func.random()).first()
    ingredients = Ingredients.query.filter_by(uuid=recipe.uuid).all()

    return render_template("random_recipe.html", recipe=recipe, ingredients=ingredients, user=current_user,
                           shopping_list=shopping_list, view_id=recipe.uuid)


@views.route('/view_recipe/<recipe_uuid>', methods=['POST', 'GET'])
@login_required
def view_recipe(recipe_uuid):
    ''' View a specific recipe in detail. '''
    if request.method == 'POST':
        category = request.form.getlist('category')
        ingredient_list = request.form.getlist('ingredients')
        for ingredient in ingredient_list:
            ingredient = ShoppingList(shopping_item=ingredient, category=category[ingredient_list.index(ingredient)])
            db.session.add(ingredient)
            db.session.commit()

    shopping_list = ShoppingList.query.count()

    recipe_id = recipe_uuid
    recipe = Recipe.query.filter_by(uuid=recipe_id).first()
    ingredients = Ingredients.query.filter_by(uuid=recipe_uuid).all()
    instructions_json = json.loads(recipe.instructions_json)

    return render_template("view_recipe.html", recipe=recipe, ingredients=ingredients, user=current_user,
                           shopping_list=shopping_list, view_id=recipe_id, instructions_json=instructions_json)


@views.route('/edit_recipe/<recipe_uuid>', methods=['POST', 'GET'])
@login_required
def edit_recipe(recipe_uuid):
    ''' Edits and updates an existing recipe. '''

    if request.method == 'POST':
        tags = request.form.getlist('edited_tags')
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
                new_tag = Tag(tag_name=str(tag).upper())
                recipe_update.tags.append(new_tag)

                db.session.add(new_tag)

        db.session.commit()

        return redirect(url_for('views.view_recipe', recipe_uuid=recipe_uuid))

    shopping_list = ShoppingList.query.count()

    recipe_id = recipe_uuid
    recipe = Recipe.query.filter_by(uuid=recipe_id).first()
    instructions_json = json.loads(recipe.instructions_json)
    ingredients = Ingredients.query.filter_by(uuid=recipe_uuid).all()

    return render_template("edit_recipe.html", recipe=recipe, ingredients=ingredients, user=current_user,
                           shopping_list=shopping_list, view_id=recipe_id, instructions_json=instructions_json)


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
    
    if request.method == 'POST':
        category = request.form.get('ing_type')
        ingredient = request.form.get('ingredient')

        ingredient_to_add = ShoppingList(shopping_item=ingredient, category=category)
        db.session.add(ingredient_to_add)
        db.session.commit()

        return redirect(url_for('views.cart'))

    shopping_list = ShoppingList.query.count()
    shopping_items_pasta = ShoppingList.query.filter_by(category='pasta').all()
    shopping_items_produce = ShoppingList.query.filter_by(category='produce').all()
    shopping_items_misc = ShoppingList.query.filter_by(category='misc').all()
    shopping_items_dairy = ShoppingList.query.filter_by(category='dairy_bread').all()
    shopping_items_meat = ShoppingList.query.filter_by(category='meat').all()
    shopping_items_frozen = ShoppingList.query.filter_by(category='frozen').all()
    shopping_items_coffee = ShoppingList.query.filter_by(category='coffee_tea').all()

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
                           coffee_to_copy=coffee_to_copy)


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

