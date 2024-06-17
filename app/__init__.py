from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your key' # can be rempoved
app.config['MONGO_URI'] = 'mongodb://localhost:27017/eBlog'
mongo = PyMongo(app)

from app import routes