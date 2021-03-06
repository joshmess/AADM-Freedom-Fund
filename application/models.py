# importing db from init file
from . import db
from flask_login import UserMixin

# inherit from db model and flash login


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class Prisoner(db.Model):
    __bind_key__ = 'prisoners'
    id = db.Column(db.Integer(), primary_key=True, unique=True)
    arresting_agency = db.Column(db.String(length=6), nullable=False, unique=False)
    grade_of_charge = db.Column(db.String(length=1), nullable=False, unique=False)
    charge_description = db.Column(db.String(length=1024), nullable=False, unique=False)
    bond_amount = db.Column(db.Float(), nullable=True, unique=False)
    disqualifies = db.Column(db.Boolean(), nullable=False, unique=False)
    mid = db.Column(db.Integer(), nullable=False, unique=False)
    name = db.Column(db.String(), nullable=False, unique=False)
    url = db.Column(db.String(), nullable=False, unique=False)
    qualifies = db.Column(db.Boolean(), nullable=False, unique=False)