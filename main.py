from flask import Flask
from flask_login import LoginManager
from model.authdb import db


def create_app():
    app = Flask(__name__)

    db.create_all()

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from model.authdb import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return db.query(User).get(int(user_id))

    # blueprint for auth routes in our app
    from controller.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from controller.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    app.run(debug=True, host="0.0.0.0", port=5696)

if __name__ == '__main__':
    create_app()