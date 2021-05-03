from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)


@auth.route('login', methods=['GET', 'POST'])
def login():
    data = request.form
    print(data)
    if request.method == "POST":
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # add data validation here
        if len(username) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            flash('Account Created!', category="success")
            print("Success")
            return redirect(url_for('views.home'))
    return render_template("login.html")


@auth.route('logout')
def logout():
    return "<p>Logout</p>"
