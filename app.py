import random
from flask import Flask, render_template, request, make_response, redirect, url_for, flash
from flask_pymongo import PyMongo
import bcrypt
import json
from bson.objectid import ObjectId
from datetime import datetime
from bson.json_util import dumps, loads
from urllib.parse import urlsplit, parse_qs

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://admin:password123@ds147942.mlab.com:47942/ks-hack"
mongo = PyMongo(app)
users_db = mongo.db.users
posts_db = mongo.db.posts

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/user_dashboard')
def userDashboard():
    return render_template('user_dashboard.html')

@app.route('/class_dashboard')
def classDashboard():
    return render_template('class_dashboard.html')

# @app.route('/dashboard')
# def dash():
#     return render_template('dashboard.html')

@app.route('/api/register', methods=['POST'])
def authRegister():
    data = request.form
    # encryptedPassword = bytes(data['password'], encoding="utf-8")
    search = users_db.find_one({"email" : data["email"]})
    if search:
        return "There already exists an account with this email."
    else:
        # hashedPassword = bcrypt.generate_password_hash(encryptedPassword)
        user = {"name": data['name'], "email": data['email'], "password": data['password'], "class_ids": [], "points": 0, "post_ids": []}
        result = users_db.insert_one(user)
        return redirect('/')
        # return "User has been successfully created"

@app.route('/api/login', methods=['POST'])
def authLogin():
    data = request.form
    # encryptedPassword = bytes(data['password'], encoding="utf-8")
    search = users_db.find_one({"email" : data["email"]})
    if search:
        id = search["_id"]
        hashedPassword = search["password"]
        # if the encryptedPassword matches the hashedPassword
        # if bcrypt.check_password_hash(encryptedPassword, hashedPassword):
        if data['password'] == hashedPassword:
            return redirect('/user_dashboard')
            # return redirect('/dashboard')
            # res = make_response(redirect('/user_dashboard'))
    #         # one day long cookie
            # res.set_cookie('uuid', str(id), max_age = 60*60*24)
            # return res;
        else:
            print("incorrect password")
            return redirect('/login')
    else:
        print("user not found")
        return redirect('/login')
    # return redirect('/user_dashboard')

@app.route('/logout')
def logout():
    res = make_response(redirect('/'))
    res.delete_cookie('uuid')
    return res

@app.route('/api/posts', methods=['POST'])
def getPosts():
    data = json.loads(request.data)
    userId = ObjectId(data['uuid'])
    search = users_db.find_one({"_id": userId})
    posts = search["posts"]
    return json.dump(posts)

@app.route('/api/addPoints', methods=['POST'])
def addPoints():
    data = json.loads(request.data)
    postId = ObjectId(data["uuid"])
    posts_db.find_one_and_update({"_id": postId}, {"points": data["points"]+1})
    return redirect('/')


if __name__ == '__main__':
    app.run()
