import os
from flask import Blueprint, flash, render_template, redirect, url_for, request
from website.forms import RegisterForm, LoginForm, ProfilePictureForm, UpdateInfoForm
from .models import User, Discussion, Message
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from functools import wraps
from werkzeug.utils import secure_filename
import random

auth = Blueprint('auth', __name__)

def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.is_anonymous:
                return render_template('errors/403.html')
            else:
                if current_user.role not in roles:
                    return render_template('errors/403.html')
            return f(*args, **kwargs)
        return wrapped
    return wrapper

def generate_username():
    random_numbers = ''.join(random.choice('0123456789') for _ in range(3))
    return f'user{random_numbers}'

def generate_email(username):
    return f'{username}@email.com'

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = RegisterForm()

    username = generate_username()
    while User.query.filter_by(username=username).first():
        username = generate_username()
    
    email = generate_email(username=username)

    if form.validate_on_submit():
        username = form.username.data
        email =  form.email.data
        new_user = User(role='user', username=username, email=email, password=generate_password_hash(form.password1.data), profile_picture='default.jpg')
        db.session.add(new_user)
        db.session.commit()
        # return render_template('login.html', form=form, filled_data=request.form, username=username, email=email)
        return redirect(url_for('auth.login'))
    else:
        print("Validation errors:", form.errors)

    return render_template('sign_up.html', form=form, filled_data=request.form, username=username, email=email)



@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in Successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password. Try again.', category='error')
        else:
            flash('Email does not exists', category='error')

    return render_template('login.html', form=form, filled_data=request.form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfilePictureForm()

    if form.validate_on_submit():
        print(form.data)
        picture = form.profile_picture.data
        if picture:
            filename = secure_filename(picture.filename)
            file_path = os.path.join('website/static/images/user_icon', filename)
            print(file_path)
            picture.save(file_path)

            current_user.profile_picture = filename
            db.session.commit()

            flash('Profile picture updated!', 'success')

            return redirect(url_for('auth.profile'))

    return render_template('profile.html', form=form, username=current_user.username, email=current_user.email)

@auth.route('/update-info', methods=['GET', 'POST'])
@login_required
def update_info():
    form = UpdateInfoForm()  

    if form.validate_on_submit():

        user_username = User.query.filter_by(username=form.username.data).first()
        if user_username and form.username.data!=current_user.username:
            flash('Username is already taken.')
            return render_template('update_info.html', form=form)
        user_email = User.query.filter_by(email=form.email.data).first()
        if user_email and form.email.data!=current_user.email:
            flash('Email already exists.')
            return render_template('update_info.html', form=form)

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()

        flash('Your information has been updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('update_info.html', form=form)

@auth.route('/admin')
@requires_roles('admin')
@login_required
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)

@auth.route('/admin/<int:user_id>/delete_user', methods=['POST'])
@requires_roles('admin')
@login_required
def delete_user(user_id):
    if current_user.role == 'admin':
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('auth.admin'))