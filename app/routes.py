from flask import render_template, request, redirect, url_for, flash,session # session for login
from . import app, mongo
from werkzeug.security import generate_password_hash,check_password_hash # for passord hashing 
from .models import User, Post
from datetime import datetime
from bson import ObjectId  # Import ObjectId from bson
@app.route('/')
def index():
    posts = mongo.db.posts.find()
    for post in posts:
        post['formatted_timestamp'] = post['timestamp'].strftime('%d %B %Y %H:%M:%S')
    return render_template('index.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # if username exists in database
        user = mongo.db.users.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            # successful login , setting session variables
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Incorrect username or password', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    # clear session variables
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'logged_in' in session:
        username = session['username']
        posts = list(mongo.db.posts.find({'author': username}))
        for post in posts:
            post['formatted_timestamp'] = post['timestamp'].strftime('%d %B %Y %H:%M:%S')

        return render_template('profile.html', username=username,posts=posts)
    else:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        #if username or email already exists
        existing_user = mongo.db.users.find_one({'$or': [{'username': username}, {'email': email}]})
        if existing_user:
            flash('Username or email already exists', 'error')
            return redirect(url_for('register'))
        
        # hashing the password
        hashed_password = generate_password_hash(password)

        #new User instance
        new_user = User(username=username, email=email, password=hashed_password)

        # inserting new user into MongoDB
        mongo.db.users.insert_one(new_user.to_dict())

        flash('Registration successful', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/post/<post_id>')
def view_post(post_id):
    # change post_id from string to ObjectId
    post_id_obj = ObjectId(post_id)
    post = mongo.db.posts.find_one_or_404({'_id': post_id_obj})
    return render_template('post.html', post=post)


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
       
        #insertion of a new post into MongoDB
        title = request.form.get('title')
        content = request.form.get('content')
        author = session['username']  # to get logged in user

        new_post = {
            'title': title,
            'content': content,
            'author': author,
            'timestamp': datetime.now() 
            }
        mongo.db.posts.insert_one(new_post)
        flash('Post created successfully', 'success')
        return redirect(url_for('profile'))

    return render_template('create_post.html')

