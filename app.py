import random
from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_pymongo import PyMongo
import bcrypt
import json
from bson.objectid import ObjectId
from datetime import datetime
from bson.json_util import dumps, loads

app = Flask(__name__, static_folder='../static/dist', template_folder='../static')
app.config["MONGO_URI"] = "mongodb://admin:password123@ds147942.mlab.com:47942/ks-hack"
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('../templates/index.html')

if __name__ == '__main__':
    app.run()
