import random
from flask import Flask, render_template, request, make_response, redirect, url_for
from flask_pymongo import PyMongo
import bcrypt
import json
from bson.objectid import ObjectId
from datetime import datetime
from bson.json_util import dumps, loads

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://admin:password123@ds147942.mlab.com:47942/ks-hack"
mongo = PyMongo(app)
users_db = mongo.db.users

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/api/register', methods=['POST'])
def registerAuth():
    data = request.form
    encryptedPassword = bytes(data['password'], encoding="utf-8")
    search = users_db.find_one({"email" : data["email"]})
    if search:
        return "There already exists an account with this email."
    else:
        hashedPassword = bcrypt.hashpw(encryptedPassword, bcrypt.gensalt())
        user = {"name": data['name'], "email": data['email'], "password": encryptedPassword, "class_ids": [], "points": 0, "post_ids": []}
        result = users_db.insert_one(user)
        # return redirect('/')
        return "User has been successfully created"

@app.route('/api/login', methods=['POST'])
def loginAuth():
    data = request.form
    encryptedPassword = bytes(data['password'], encoding="utf-8")
    search = users_db.find_one({"email" : data["email"]})
    if search:
        id = search["_id"]
        hashedPassword = search["password"]
        # if the encryptedPassword matches the hashedPassword
        if bcrypt.checkpw(encryptedPassword, hashedPassword):
            res = make_response(redirect('/'))
            # one day long cookie
            res.set_cookie('uuid', str(id), max_age = 60*60*24)
            return res
        else:
            print("incorrect password")
    else:
        print("user not found")
    return render_template("index.html")

@app.route('/api/logout')
def logout():
    res = make_response(redirect('/'))
    res.delete_cookie('uuid')
    return res

@app.route('/api/posts', methods=['POST'])
def getPosts():
    # data = json.loads(request.data)
    print(request.form)
    return "test"


if __name__ == '__main__':
    app.run()
