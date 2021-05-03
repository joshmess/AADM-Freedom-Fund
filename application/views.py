from flask import Blueprint, render_template
from .models import User

views = Blueprint('views', __name__)


@views.route('/')
def home():
    users = User.query.all()
    return render_template("home.html", users=users)
