import random
from flask import Flask, render_template, request, make_response, redirect, url_for, flash
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

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/register', methods=['POST'])
def authRegister():
    data = request.form
    encryptedPassword = bytes(data['password'], encoding="utf-8")
    search = users_db.find_one({"email" : data["email"]})
    if search:
        return "There already exists an account with this email."
    else:
        hashedPassword = bcrypt.hashpw(encryptedPassword, bcrypt.gensalt())
        user = {"name": data['name'], "email": data['email'], "password": encryptedPassword, "class_ids": [], "points": 0, "post_ids": []}
        result = users_db.insert_one(user)
        return redirect('/')
        # return "User has been successfully created"

@app.route('/api/login', methods=['POST'])
def authLogin():
    data = request.form
    encryptedPassword = bytes(data['password'], encoding="utf-8")
    search = users_db.find_one({"email" : data["email"]})
    # if search:
        # id = search["_id"]
        # hashedPassword = search["password"]
        # if the encryptedPassword matches the hashedPassword
        # if bcrypt.checkpw(encryptedPassword, hashedPassword):
            # return redirect('/dashboard')
    #         res = make_response(redirect('/'))
    #         # one day long cookie
    #         res.set_cookie('uuid', str(id), max_age = 60*60*24)
    #         return res;
        # else:
            # print("incorrect password")
    # else:
        # print("user not found")
    return redirect('/dashboard')

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


@app.route('/api/addClass', methods=['POST'])
def addClass():
    data = json.loads(request.data)
    course_id = data["course_id"]
    user_id = data["user_id"]
    class_ids = users_db.find_one({"_id": ObjectId(user_id)})["class_ids"]
    class_ids.append(course_id)
    result = users_db.find_one_and_update({"_id": ObjectId(user_id)}, {"$set": {"class_ids": class_ids}})
    return "done"




if __name__ == '__main__':
    app.run()
