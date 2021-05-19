"""Main app/routing file for Twittoff"""

from os import getenv
from flask import Flask, render_template
from .models import DB, User
from .twitter import add_or_update_user


def create_app():
    """Create an instance of the flask application"""
    app = Flask(__name__)
    users = User.query.all()

    app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    DB.init_app(app)

    @app.route('/')
    def root():
        return render_template("base.html", title="Home", users=users)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template("base.html", title="Home", users=users)
    
    @app.route('/populate')
    def populate():
        add_or_update_user("elonmusk")
        add_or_update_user("jackblack")
        return render_template("base.html", title="Home", users=users)

    return app


# def insert_users(usernames):
#     for id_index, username in enumerate(usernames):
#         user = User(id=id_index, username=username)
#         DB.session.add(user)
#         DB.session.commit()