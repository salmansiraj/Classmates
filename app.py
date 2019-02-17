import random
from flask import Flask, render_template, request, make_response, redirect, url_for, flash, session
from flask_pymongo import PyMongo
import bcrypt
import json
from bson.objectid import ObjectId
from datetime import datetime
from bson.json_util import dumps, loads
from urllib.parse import urlsplit, parse_qs
from functools import wraps
import tinys3


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://admin:password123@ds147942.mlab.com:47942/ks-hack"
mongo = PyMongo(app)
users_db = mongo.db.users
posts_db = mongo.db.posts
classes_db = mongo.db.classes
# conn = tinys3.Connection("AKIAIZFZLZYJI6PKG6YA", "7gT3u4UT2BpAf99ALVjVT3SL/LnG2n0kVXnXjeHo", tls=True, endpoint='s3-us-east-2.amazonaws.com')

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Connection with tinys3
conn = tinys3.Connection("AKIAIZFZLZYJI6PKG6YA","7gT3u4UT2BpAf99ALVjVT3SL/LnG2n0kVXnXjeHo", default_bucket='coursemates')

# Should be hashed so that previous files or images can't be overwritten
# f = open('static/img/bg-masthead.jpg','rb')
# r = conn.upload('static/img/bg-masthead.jpg',f)



def login_required(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if not 'user_id' in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return dec

@app.route('/')
def index():
    if 'user_id' in session:
        # user is logged in
        return redirect(url_for('user_dashboard'))
    return render_template('index.html')

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    result = users_db.find_one({"_id": ObjectId(session['user_id'])})
    class_ids = result['class_ids']
    classes = []
    for class_id in class_ids:
        courseInfo = classes_db.find_one({"_id": ObjectId(class_id)})
        classes.append(courseInfo)
    return render_template('user_dashboard.html', classes=classes)

@app.route('/class/<course_id>')
@login_required
def course(course_id):
    result = classes_db.find_one({"_id": ObjectId(course_id)})
    posts = posts_db.find({"class": course_id})
    postData = []
    for post in posts:
        postData.append(post)
    return render_template('class_dashboard.html', courseInfo = result, posts = postData)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

# @app.route('/user_dashboard')
# def userDashboard():
#     return render_template('user_dashboard.html')

@app.route('/class_dashboard')
def classDashboard():
    return render_template('class_dashboard.html')


@app.route('/create_post/<course_id>')
def createPostPage(course_id):
    return render_template('create_post.html', user_id = str(session["user_id"]), course_id = course_id)

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
        return redirect('/login')
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
            session["user_id"] = str(id)
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
    session.pop('user_id', None)
    res = make_response(redirect('/'))
    return res

# @app.route('/api/posts', methods=['POST'])
# def getPosts():
#     data = json.loads(request.data)
#     userId = ObjectId(data['uuid'])
#     search = users_db.find_one({"_id": userId})
#     posts = search["posts"]
#     return json.dump(posts)

@app.route('/api/getCoursePosts')
def getCoursePosts():
    data = json.load(request.data)
    course_id = data["course_id"]
    result = posts_db.find({"class": course_id})
    return dumps(result) if result else {}

@app.route('/api/getUserCourses')
def getUserCourses():
    data = json.load(request.data)
    user_id = data["user_id"]
    result = users_db.find_one({"_id": ObjectId(user_id)})
    return dumps(result) if result else {}

@app.route('/api/addPoints/<post_id>', methods=['POST'])
def addPoints(post_id):
    result = posts_db.find_one({"_id": ObjectId(post_id)})
    currentPoints = result["points"]
    currentPoints += 1
    result2 = posts_db.update({"_id": ObjectId(post_id)}, {"$set": {"points": currentPoints}})
    return json.dumps({"status": "ok"})

@app.route('/api/decreasePoints/<post_id>', methods=['POST'])
def decreasePoints(post_id):
    result = posts_db.find_one({"_id": ObjectId(post_id)})
    currentPoints = result["points"]
    currentPoints -= 1
    result2 = posts_db.update({"_id": ObjectId(post_id)}, {"$set": {"points": currentPoints}})
    return json.dumps({"status": "ok"})

# @app.route('/class/<course_id>')
# def course(course_id):
#     result = classes_db.find_one({"_id": ObjectId(course_id)})
#     posts = posts_db.find({"class": course_id})
#     postData = []
#     for post in posts:
#         postData.append(post)
#     return render_template('class_dashboard.html', courseInfo = result, posts = postData)

# endpoint to add classes
@app.route('/api/addClass', methods=['POST'])
def addClass():
    data = json.loads(request.data)
    for courseName in data:
        courseObject = {"course_name": courseName, "professor": "nobody", "student_ids": [], "post_ids": []}
        result = classes_db.insert_one(courseObject)
    # course = {"course_name": data['course_name'], "professor": "nobody", "student_ids": [], "post_ids": []}
    # result = classes_db.insert_one(course)
    return redirect('/')

@app.route('/api/addPost', methods=['POST'])
def addPost():
    data = json.loads(request.data)
    result = posts_db.insert_one({"filepath": data['image_name'], "class": data["course_id"], "content": data["name"], "comment": data["caption"], "student_id": data["user_id"], "points": 0})
    result2 = users_db.find_one_and_update({"_id": ObjectId(data["user_id"])}, {"$push": {"post_ids": result.inserted_id}})
    f = open('static/img/' + data['image_name'],'rb')
    r = conn.upload('static/img/' + data['image_name'],f)
    return "ok"

#  endpoint to find class information with class name
# @app.route('/api/findClass', methods=['POST'])
# def findClass():
#     data = json.loads(request.data)
#     print(data)



# @app.route('/api/addPost', methods=['POST'])
# def addPost():
#     data = json.loads(request.data)
#     for courseName in data:
#         courseObject = {"course_name": courseName, "professor": "nobody", "student_ids": [], "post_ids": []}
#         result = classes_db.insert_one(courseObject)

#     return redirect('/')

#  endpoint to find class information with class name
# @app.route('/api/findClass', methods=['POST'])
# def findClass():
#     data = json.loads(request.data)
#     print(data)

if __name__ == '__main__':
    app.run()
