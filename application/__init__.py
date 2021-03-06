# makes the python folder a package
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "User.db"
PRISONER_DB_NAME = "Prisoners.db"


def create_app():

    # __name__ is the name of the current module (name of file ran)
    app = Flask(__name__)

    # encrypt secure cookies and session data
    # don't share when we deploy
    app.config['SECRET_KEY'] = "AADM-SWE"

    # instantiating SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_BINDS'] = {
        "prisoners": f'sqlite:///{PRISONER_DB_NAME}'
    }
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    create_database(app)

    return app


def create_database(app):
    if not path.exists("application/" + DB_NAME):
        db.create_all(app=app)
        print("Created Database!")

    if not path.exists("application/" + PRISONER_DB_NAME):
        db.create_all(bind="prisoners", app=app)
        print("Created Prisoner Database!")
