from flask import Flask, Blueprint, render_template, request, jsonify, redirect, url_for
from model.model import Database
from model.model import RecipeAPI
from flask_login import AnonymousUserMixin
from controller.auth import current_user, get_username
import json
database = Database()
recipeapi = RecipeAPI()

main = Blueprint('main',__name__, template_folder='../templates')

@main.route('/')
def index():
    recipes_random = database.random_recipes(5)
    for recipe in recipes_random:
        recipe['Steps'] = json.loads(recipe['Steps'])
        recipe['Ingredients'] = database.get_ingredients(recipe["RecName"])
        recipe['youtube_link'] = recipeapi.get_youtubelink_parser(recipe['RecName'])
    if isinstance(current_user, AnonymousUserMixin):
            name = None
            email = None
            picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
    return render_template('index.html', active_page='home', recipes=recipes_random, name=name, email=email, picture=picture)

@main.route('/add_recipes', methods=['GET', 'POST'])
def api_recipes():
    parsed_recipes = []
    if request.method == 'POST':
        search_term = request.form.get('search')
        search_results = recipeapi.lookup_recipe(search_term)
        parsed_recipes = recipeapi.parse_recipe(search_results)
        #print(parsed_recipes)
        return jsonify(recipes=parsed_recipes)
    else:
        if isinstance(current_user, AnonymousUserMixin):
            name = None
            email = None
            picture = None
        else:
            name = current_user.name
            email = current_user.email
            picture = current_user.picture
        ingredients = database.get_all_ingredients()
        return render_template('add_recipes.html', active_page='add_recipes', recipes=parsed_recipes, name=name, email=email, ingredients=ingredients, picture=picture)

@main.route('/recipe_info', methods=['POST'])
def recipe_info():
    recipe = request.get_json().get('recipe')
    return jsonify(status="success")

@main.route('/add_recipe', methods=['POST'])
def add_recipe():
    recipe = request.get_json()
    database.insert_recipe(recipe, get_username(current_user.email))
    return jsonify(success=True)

@main.route('/select_recipe', methods=['POST'])
def select_recipe():
    recipe = request.get_json()
    database.insert_recipe(recipeapi.parse_recipe(recipeapi.lookup_recipe(recipe['name']))[0], get_username(current_user.email))
    return jsonify(success=True)

@main.route('/browse_db', methods=['POST'])
def browse_db():
    search_term = request.form.get('search')
    recipes = database.browse_main_table(search_term)
    return jsonify(recipes = recipes)

@main.route('/update_recipe_form', methods=['POST'])
def update_recipe_form():
    if isinstance(current_user, AnonymousUserMixin):
            name = None
            email = None
            picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
        
    recName = request.form.get('recipeName')
    ingredients = database.get_all_ingredients()
    recipe = database.browse_main_table(recName)
    return render_template('update_recipe.html', active_page='update_recipe', recipe=recipe, ingredients=ingredients, name=name, email=email, picture=picture)

        
@main.route('/update_recipe', methods=['POST'])
def update_recipe():
    if isinstance(current_user, AnonymousUserMixin):
            name = None
            email = None
            picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
        
    recipe = request.get_json()
    database.update_recipe(recipe, get_username(email))
    return redirect(url_for('main.my_recipes'))
        

@main.route('/save_recipe', methods=['POST'])
def save_recipe():
    recipe = request.get_json()
    database.add_to_saved(recipe['name'], get_username(current_user.email))
    return jsonify(success=True)

@main.route('/delete_recipe', methods=['POST'])
def delete_recipe():
    recipe = request.form.get('recipeName')
    database.delete_recipe(recipe)
    return redirect(url_for('main.my_recipes'))

#Route that gets called by a script in "saved recipes" to delete a saved recipe from a User
@main.route('/delete_saved_recipe',methods=['POST'])
def delete_saved_recipe():
    print("WE ARE HERE")
    if not isinstance(current_user, AnonymousUserMixin):
        email = current_user.email
        recipe_name = request.json['name']
        database.delete_saved_recipe(recipe_name,get_username(email))
    return jsonify({'status': 'success'})

@main.route('/delete_my_ingredient',methods=['POST'])
def delete_my_ingredient():
    print("WE ARE HERE")
    if not isinstance(current_user, AnonymousUserMixin):
        email = current_user.email
        print(request.json)
        ingredient_name = request.json['ingredient']
        database.remove_owned_ingredient(get_username(email), ingredient_name)
    return jsonify({'status': 'success'})

@main.route('/delete_my_allergy',methods=['POST'])
def delete_my_allergy():
    print("WE ARE HERE")
    if not isinstance(current_user, AnonymousUserMixin):
        email = current_user.email
        allergy_name = request.json['allergy']
        database.remove_allergies(get_username(email), allergy_name)
    return jsonify({'status': 'success'})

@main.route('/saved_recipes')
def saved_recipes():
    if isinstance(current_user, AnonymousUserMixin):
            name = None
            email = None
            picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
        recipes = database.show_saved_recipes(get_username(email))
        for recipe in recipes:
            recipe['Steps'] = json.loads(recipe['Steps'])
            recipe['youtube_link'] = recipeapi.get_youtubelink_parser(recipe['RecName'])
            recipe['Allergy'] = database.contains_allergies(recipe["RecName"],get_username(email))
            recipe['Sufice'] = database.check_sufficient_ingredients(recipe["RecName"],get_username(email))
    return render_template('saved_recipes.html', active_page='saved_recipes', name=name, email=email, picture=picture, recipes=recipes)

@main.route('/my_recipes')
def my_recipes():
    if isinstance(current_user, AnonymousUserMixin):
            name = None
            email = None
            picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
        recipes = database.get_my_recipes(get_username(email))
        for recipe in recipes:
            recipe['Steps'] = json.loads(recipe['Steps'])
            recipe['youtube_link'] = recipeapi.get_youtubelink_parser(recipe['RecName'])
    return render_template('my_recipes.html', active_page='my_recipes', name=name, email=email, picture=picture, recipes=recipes)

@main.route('/browse_recipes')
def browse_recipes():
    if isinstance(current_user, AnonymousUserMixin):
        name = None
        email = None
        picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
        recipes = database.get_my_recipes(get_username(email))
        for recipe in recipes:
            recipe['Steps'] = json.loads(recipe['Steps'])
            recipe['youtube_link'] = recipeapi.get_youtubelink_parser(recipe['RecName'])
    return render_template('browse_recipes.html', active_page='browse_recipes', name=name, email=email, picture=picture)

@main.route('/manage_ingredients', methods=['GET', 'POST'])
def store_ingredients():
    if isinstance(current_user, AnonymousUserMixin):
            name = None
            email = None
            picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
    if request.method == 'POST':
        # Check if the request has JSON data
        if request.is_json:
            data = request.get_json()
            ingName = data.get('search')
        else:
            ingName = request.form.get('search')
        database.add_owned_ingredient(get_username(email), ingName)
        return jsonify(success=True)
    else:
        myIngredients = database.get_owned_ingredients(get_username(email))
        myAllergies = database.get_allergies(get_username(email))
        ingredients = database.get_all_ingredients()
        return render_template('manage_ingredients.html', active_page='manage_ingredients', name=name, email=email, ingredients=ingredients, myIngredients=myIngredients, myAllergies = myAllergies, picture=picture)


@main.route('/manage_allergies', methods=['POST'])
def store_allergies():
    if isinstance(current_user, AnonymousUserMixin):
            name = None
            email = None
            picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
    if request.method == 'POST':
        # Check if the request has JSON data
        if request.is_json:
            data = request.get_json()
            ingName = data.get('search')
        else:
            ingName = request.form.get('search')
        database.add_allergies(get_username(email), ingName)
        return jsonify(success=True)


@main.route('/menus',methods=['GET', 'POST'])
def menus():
    if current_user.is_anonymous:
        name = None
        email = None
        picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture

    select_from = [i["RecName"] for i in database.show_saved_recipes(get_username(email))]

    selected_option = request.form.get('select') if request.method == 'POST' else None

    raw_menus = database.get_menus(get_username(email))
    print("Raw Menus:", raw_menus)

    menus = {}
    for menu_name, menu_items in raw_menus.items():
        print("Processing menu:", menu_name)  # Print the current menu name
        for item in menu_items:
            description = item[0]
            recipe_name = item[1]
            menus.setdefault(menu_name, []).append([description, recipe_name])
            print("Added to menus:", [description, recipe_name])  # Print what's added to menus

    rendered_template = render_template('menus.html', active_page='menus', name=name, email=email, picture=picture, select_from=select_from, selected_option=selected_option, menus=menus)

    return rendered_template

@main.route('/add_to_menu', methods=['POST'])
def add_to_menu():
    data = request.get_json()
    if 'menuName' in data and 'recipeName' in data and 'description' in data:
        menuName = data['menuName']
        recipeName = data['recipeName']
        description = data['description']  # Get the description from the request data
        username = get_username(current_user.email)
        database.insert_menu(username, recipeName, menuName, description)
        return jsonify(success=True)
    else:
        return jsonify(success=False, message="menuName, recipeName or description not provided in request")

@main.route('/delete_single_menu',methods=['POST'])
def delete_single_menu():
    data = request.get_json()
    menu_name = data['name']
    username = get_username(current_user.email)
    database.delete_entire_menu(menu_name,username)
    return jsonify({'status': 'success'})

@main.app_errorhandler(400)
def bad_request(e):
    if isinstance(current_user, AnonymousUserMixin):
        name = None
        email = None
        picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
    return render_template('error.html', error_code=400, message="Bad request", name=name, email=email, picture=picture), 400

@main.app_errorhandler(401)
def unauthorized(e):
    if isinstance(current_user, AnonymousUserMixin):
        name = None
        email = None
        picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
    return render_template('error.html', error_code=401, message="Unauthorized", name=name, email=email, picture=picture), 401

@main.app_errorhandler(403)
def forbidden(e):
    if isinstance(current_user, AnonymousUserMixin):
        name = None
        email = None
        picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
    return render_template('error.html', error_code=403, message="Forbidden", name=name, email=email, picture=picture), 403

@main.app_errorhandler(405)
def method_not_allowed(e):
    if isinstance(current_user, AnonymousUserMixin):
        name = None
        email = None
        picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
    return render_template('error.html', error_code=405, message="Method not allowed", name=name, email=email, picture=picture), 405

@main.app_errorhandler(404)
def page_not_found(e):
    if isinstance(current_user, AnonymousUserMixin):
        name = None
        email = None
        picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
    return render_template('error.html', error_code=404, message="Page not found", name=name, email=email, picture=picture), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    if isinstance(current_user, AnonymousUserMixin):
        name = None
        email = None
        picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
    return render_template('error.html', error_code=500, message="Internal server error", name=name, email=email, picture=picture), 500

@main.app_errorhandler(503)
def service_unavailable(e):
    if isinstance(current_user, AnonymousUserMixin):
        name = None
        email = None
        picture = None
    else:
        name = current_user.name
        email = current_user.email
        picture = current_user.picture
    return render_template('error.html', error_code=503, message="Service unavailable", name=name, email=email, picture=picture), 503