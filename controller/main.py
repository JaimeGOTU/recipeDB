from flask import Flask, Blueprint, render_template
#from flask_simplelogin import SimpleLogin

main = Blueprint('main',__name__, template_folder='../templates')
#SimpleLogin(app)

@main.route('/')
def index():
    return render_template('index.html', active_page='home')

@main.route('/add_recipes')
def add_recipes():
    return render_template('add_recipes.html', active_page='add_recipes')

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