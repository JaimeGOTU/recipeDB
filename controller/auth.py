# auth.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from model.authdb import User, db
from model.model import Database
import os


auth = Blueprint('auth', __name__, template_folder='../templates')
recipeDB = Database()

def get_username(email):
    return email.split('@')[0]

@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = db.query(User).filter_by(email=email).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login credentials and try again.')
        return redirect(url_for('auth.login'))  # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    flash('You have been logged in.')
    return redirect(url_for('main.index'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')

print(os.getcwd())

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    userparams = (get_username(email), email)
    picture = request.files['image']
    
    if not os.path.exists('static\\images\\uploads\\'):
        os.makedirs('static\\images\\uploads\\')

    # handle the image upload
    if 'image' not in request.files:
        flash('No image part in the request.')
        return redirect(request.url)
    if picture.filename == '':
        flash('No selected image.')
        return redirect(request.url)
    if picture:
        filename = secure_filename(picture.filename)
        filepath = f"../static/images/uploads/{filename}"
        picture.save(os.path.join('static\\images\\uploads', filename))

    user = db.query(User).filter_by(email=email).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password), picture=filepath)

    # add the new user to the database
    db.add(new_user)
    db.commit()

    recipeDB.insert_user(userparams)

    return redirect(url_for('auth.login'))


@auth.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, email=current_user.email, picture=current_user.picture)

@auth.route('/delete_account',methods=['GET'])
def delete_account():
    
    # Query for the user
    user_to_delete = db.query(User).filter(User.email == current_user.email).first()

    # Check if the user exists
    if user_to_delete:
        # Delete the user
        db.delete(user_to_delete)

        # Commit the transaction
        db.commit()

    return redirect(url_for('main.index'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))