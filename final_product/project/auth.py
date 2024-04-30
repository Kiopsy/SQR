from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User
from . import db, certificate_authority

# Define a Blueprint for the authentication routes
auth = Blueprint("auth", __name__)

# Route for displaying the login page
@auth.route('/login')
def login():
    return render_template('login.html')

# Route for handling login form submission
@auth.route('/login', methods=['POST'])
def login_post():
    # Retrieve login form data
    name = request.form.get('name')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    # Check if the user exists and the password is correct
    user = User.query.filter_by(name=name).first()
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))  # Reload the page if login fails

    # Log in the user
    login_user(user, remember=remember)
    return redirect(url_for('main.create'))

# Route for displaying the signup page
@auth.route('/signup')
def signup():
    return render_template('signup.html')

# Route for handling signup form submission
@auth.route('/signup', methods=['POST'])
def signup_post():
    # Retrieve signup form data
    public_key = request.form.get('public_key')
    name = request.form.get('name')
    password = request.form.get('password')

    # Check if the public key already exists in the database
    user = User.query.filter_by(public_key=public_key).first()
    if user:
        flash('This public key already exists')
        return redirect(url_for('auth.signup'))  # Redirect to signup page if public key exists

    # Create a new user with hashed password
    new_user = User(public_key=public_key, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'))

    # Register the user with the Certificate Authority
    if not certificate_authority.register_user(public_key, name):
        flash('Failed to register user with Certificate Authority')
        return redirect(url_for('auth.signup'))  # Redirect to signup page on failure

    # Add the new user to the database and log them in
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user, remember=True)
    return redirect(url_for('main.create'))

# Route for logging out the user
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
