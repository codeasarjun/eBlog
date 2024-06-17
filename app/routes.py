from flask import render_template, request, redirect, url_for, flash,send_file,session # session for login
from . import app, mongo
from werkzeug.security import generate_password_hash,check_password_hash # for passord hashing 
from .models import User, Post
from datetime import datetime
from bson import ObjectId  # Import ObjectId from bson
from werkzeug.utils import secure_filename # for file upload
from gridfs import GridFS
import os
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
        # Initialize GridFS for file upload handling
        fs = GridFS(mongo.db)

        # Get form data
        title = request.form.get('title')
        content = request.form.get('content')
        author = session['username']  # Assuming you have the username in session

        # Handle file upload
        if 'document' in request.files:
            file = request.files['document']
            print("file name",file)
            if file.filename != '':
                try:
                    # Secure the filename before saving it
                    filename = secure_filename(file.filename)
                    print('file name',filename)
                    # Save file to GridFS
                    file_id = fs.put(file.stream, filename=filename, content_type=file.content_type)

                    # Prepare new post document with file details
                    new_post = {
                        'title': title,
                        'content': content,
                        'author': author,
                        'file_id': file_id,
                        'filename': filename,
                        'timestamp': datetime.now()
                    }

                    # Insert into MongoDB collection
                    mongo.db.posts.insert_one(new_post)

                    flash('Post created successfully', 'success')
                    return redirect(url_for('profile'))

                except Exception as e:
                    flash(f'Error uploading file: {str(e)}', 'error')
                    print("error ",str(e))
                    app.logger.error(f"Error uploading file: {str(e)}")
                    return redirect(url_for('create_post'))

        else:
            flash('No file part in the request', 'error')

    return render_template('create_post.html')



@app.route('/get_file/<file_id>')
def get_file(file_id):
    # retrieve file from GridFS using file_id
    fs = GridFS(mongo.db)
    file_object = fs.get(ObjectId(file_id))
    
    # Serve the file to the user
    filename = file_object.filename if file_object.filename else 'file'

    # Serve the file to the user
    response = send_file(file_object, as_attachment=True, attachment_filename=filename)
    return response

@app.route('/user_setting')
def user_setting():
    # need to add functionality where user can make a checkbox and then some JS or CSS should enabled
    return "Hello user"