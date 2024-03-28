from flask import Flask, render_template
#from flask_simplelogin import SimpleLogin

app = Flask(__name__, template_folder='../templates',static_folder='../beautify')
#SimpleLogin(app)

@app.route('/')
def index():
    return render_template('index.html', active_page='home')

@app.route('/add_recipes')
def add_recipes():
    return render_template('add_recipes.html', active_page='add_recipes')

@app.route('/saved_recipes')
def saved_recipes():
    return render_template('saved_recipes.html', active_page='saved_recipes')

@app.route('/my_recipes')
def my_recipes():
    return render_template('my_recipes.html', active_page='my_recipes')

@app.route('/menus')
def menus():
    return render_template('menus.html', active_page='menus')

@app.route('/login')
def login():
    return render_template('login.html', active_page='login')

@app.errorhandler(400)
def bad_request(e):
    return render_template('error.html', error_code=400, message="Bad request"), 400

@app.errorhandler(401)
def unauthorized(e):
    return render_template('error.html', error_code=401, message="Unauthorized"), 401

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, message="Forbidden"), 403

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('error.html', error_code=405, message="Method not allowed"), 405

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, message="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, message="Internal server error"), 500

@app.errorhandler(503)
def service_unavailable(e):
    return render_template('error.html', error_code=503, message="Service unavailable"), 503