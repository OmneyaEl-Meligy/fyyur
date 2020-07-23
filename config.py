import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False


# DATABASE URL 
SQLALCHEMY_DATABASE_URI = 'postgresql://omneya:omneya@localhost:5432/fyyurdb'


# Connect to the database
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)