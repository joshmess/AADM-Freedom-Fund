import csv
from flask import Blueprint, render_template, redirect, url_for
from .models import User, Prisoner
from application import db

views = Blueprint('views', __name__)


@views.route('/')
def home():
    users = User.query.all()
    return render_template("home.html", users=users)

@views.route('/prisoners')
def prisoners():
    prisoners = Prisoner.query.all()
    return render_template("prisoners.html", prisoners=prisoners)

@views.route('/load')
def load_data():
    with open("aadm_db.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        try:
            for row in csv_reader:
                print("Adding Prisoner " + str(line_count))
                if line_count == 0:
                    line_count += 1
                else:
                    line_count += 1
                    prisoner = Prisoner(
                        arresting_agency=row[1],
                        grade_of_charge=row[2],
                        charge_description=row[3],
                        bond_amount=float(row[4]),
                        disqualifies=(row[5] == 'True'),
                        mid=int(row[6]),
                        name=row[7],
                        url=row[8],
                        qualifies=(row[9] != '0')
                    )
                    db.session.add(prisoner)
                    db.session.commit()

            return redirect(url_for("/"))
        except Exception as e:
            db.session.rollback()

    return "<h1>Uploading CSV!</h1>"
