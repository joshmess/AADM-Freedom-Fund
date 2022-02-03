import csv
from flask import Blueprint, render_template, redirect, url_for
from .models import User, Prisoner
from application import db

views = Blueprint('views', __name__)


@views.route('/')
def home():
    totaljailed = Prisoner.query.all()
    return render_template("home.html", totaljailed=totaljailed)


@views.route('/prisoners')
def prisoners():
    prisoners = Prisoner.query.all()
    return render_template("prisoners.html", prisoners=prisoners)


@views.route('/load')
def load_data():
    # TODO Ability to update the database, right now it cannot update the database
    with open("aadm_db.csv", newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        try:
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    line_count += 1
                    prisoner = Prisoner(
                        id=row[0],
                        arresting_agency=row[1],
                        grade_of_charge=row[2],
                        charge_description=row[3],
                        bond_amount=convertBondAmount(row[4]),
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
            print(e)

    return "<h1>CSV LOADING</h1>"


def convertBondAmount(bond):
    """
        Remove unnecessary characters in the string to successfully convert
        it to a float. If the bond amount is not present, return None.
    """
    if bond == '$':
        return None
    else:
        return float(bond.strip('$').replace(',', ''))
