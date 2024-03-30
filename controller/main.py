Dummy_data1 = {
    "name":"Never going to give you up Spaghetti",
    "style":"Chinese",
    "onwer":"Rick",
    "source":"https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "steps": {"step1": "Boil water", "step2": "Cook spaghetti", "step3": "Prepare sauce", "step4": "Combine spaghetti and sauce"},
    "ingredients":[("water","69 ml"),("spaghetti","420gr"),("pasta sauce","269ml")]
}

Dummy_data2 = {
    "name":"You know the rules curry",
    "style":"Japanese",
    "onwer":"Rick",
    "source":"https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "steps": {"step1": "Marinate chicken", "step2": "Prepare curry base", "step3": "Cook chicken in curry base", "step4": "Serve with rice"},
    "ingredients":[("chicken","300gr"),("rice","500gr"),("curry base", "2 spoons")]
}

Dummy_data3 = {
    "name":"And so do I patty",
    "style":"Spanish",
    "onwer":"Rick",
    "source":"https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "steps":{"step1": "Grill patty", "step2": "Assemble ingredients on bun", "step3": "Serve with fries"},
    "ingredients":[("patty","500gr"),("buns","2"),("fries","5 sticks")]
}

from flask import Flask, Blueprint, render_template, request, jsonify
from model.model import Database
from model.model import RecipeAPI
import json
#from flask_simplelogin import SimpleLogin
database = Database()
recipeapi = RecipeAPI()

main = Blueprint('main',__name__, template_folder='../templates')
#SimpleLogin(app)

@main.route('/')
def index():
    recipes_random = database.random_recipes(5)
    for recipe in recipes_random:
        recipe['Steps'] = json.loads(recipe['Steps'])
    return render_template('index.html', active_page='home', recipes=recipes_random)


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
        return render_template('add_recipes.html', active_page='add_recipes', recipes=parsed_recipes)

@main.route('/recipe_info', methods=['POST'])
def recipe_info():
    recipe = request.get_json().get('recipe')
    print(recipe)  # or do whatever you need with the recipe info
    return jsonify(status="success")

'''
@main.route('/add_recipes', methods=['GET', 'POST'])
def api_recipes():
    search_results = []
    parsed_recipes = []
    if request.method == 'POST':
        search_term = request.form.get('search')
        search_results = recipeapi.lookup_recipe(search_term)
        parsed_recipes = recipeapi.parse_recipe(search_results)
        print(parsed_recipes)
    return render_template('add_recipes.html', active_page='add_recipes', recipes=parsed_recipes)
'''

@main.route('/add_recipes', methods=['GET', 'POST'])
def add_recipe():
    parsed_recipes = []
    return render_template('add_recipes.html', active_page='add_recipes', recipes=parsed_recipes)

@main.route('/select_recipe', methods=['POST'])
def select_recipe():
    recipe = request.get_json()
    return jsonify(success=True)

@main.route('/saved_recipes')
def saved_recipes():
    return render_template('saved_recipes.html', active_page='saved_recipes')

@main.route('/my_recipes')
def my_recipes():
    return render_template('my_recipes.html', active_page='my_recipes')

@main.route('/menus')
def menus():
    return render_template('menus.html', active_page='menus')

@main.app_errorhandler(400)
def bad_request(e):
    return render_template('error.html', error_code=400, message="Bad request"), 400

@main.app_errorhandler(401)
def unauthorized(e):
    return render_template('error.html', error_code=401, message="Unauthorized"), 401

@main.app_errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, message="Forbidden"), 403

@main.app_errorhandler(405)
def method_not_allowed(e):
    return render_template('error.html', error_code=405, message="Method not allowed"), 405

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, message="Page not found"), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, message="Internal server error"), 500

@main.app_errorhandler(503)
def service_unavailable(e):
    return render_template('error.html', error_code=503, message="Service unavailable"), 503