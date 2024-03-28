import os
from sqla_wrapper import SQLAlchemy
from flask_login import UserMixin

# this connects to a MySQL database either on Heroku or on localhost
db = SQLAlchemy(os.getenv("DATABASE_URL", "mysql+pymysql://root:4iqX0rBR2IdLx2udnc8qwcYyGGh1vhPC@192.168.9.2:3369/recAccount"))  

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(512))
    name = db.Column(db.String(1000))

