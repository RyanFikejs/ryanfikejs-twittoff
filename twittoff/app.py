"""Main app/routing file for Twittoff"""

from os import getenv
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import add_or_update_user
from .predict import predict_user


def create_app():
    """Create an instance of the flask application"""
    app = Flask(__name__)
    
    # Create different configs for heroku deployment (postgresql) vs. local (sqlite3)
    HEROKU_DEP = getenv("HEROKU_DEP")
    # Herkou still defaults the deprecated prefix in the database url, replace it
    if HEROKU_DEP:
        app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL").replace('postgres://', 'postgresql://')
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    DB.init_app(app)

    @app.route('/')
    def root():
        DB.create_all()
        return render_template("base.html", title="Home", users=User.query.all())

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template("base.html", title="Home", users=User.query.all())
    
    @app.route('/user', methods=["POST"])
    @app.route('/user/<name>', methods=["GET"])
    def user(name=None, message=''):
        name = name or request.values["user_name"]
        try:
            if request.method == "POST":
                add_or_update_user(name)
                message = f"User {name} succesfully added!"
        
            tweets = User.query.filter(User.username == name).one().tweets

        except Exception as e:
            message = f"Error handling {name}: {e}"
            tweets = []

        return render_template('user.html',
                               title=name,
                               tweets=tweets,
                               message=message
                               )

    @app.route('/compare', methods=["POST"])
    def compare():
        user0, user1 = sorted([request.values['user0'],
                                request.values['user1']
                                ])

        hypo_tweet_text = request.values["tweet_text"]

        if user0 == user1:
            message = "Cannot compare users to themselves!"
            # TODO: change the functionality of the drop down tabs in
            # the web app to not allow this to happen.

        else:
            prediction = predict_user(user0, user1, hypo_tweet_text)

            message = '"{}" is more likely to be said by \
                {} than {}'.format(hypo_tweet_text,
                                    user1 if prediction else user0,
                                    user0 if prediction else user1
                                    )

        return render_template('prediction.html',
                                title='Prediction',
                                message=message
                                )

    @app.route('/populate')
    def populate():
        add_or_update_user("elonmusk")
        add_or_update_user("jackblack")

        return render_template("base.html", title="Home", users=User.query.all())

    # TODO: Update all users when button is clicked
    @app.route('/update')
    def update():
        for user in users:
            add_or_update_user(user)
        
        return render_template('base.html',
                               title="All users' tweets updated!",
                               users=User.query.all()
                               )


    # @app.route('/iris')
    # def iris():
    #     from sklearn.datasets import load_iris
    #     from sklearn.linear_model import LogisticRegression
    #     X, y = load_iris(return_X_y=True)
    #     clf = LogisticRegression(random_state=73,
    #                              solver='lbfgs',
    #                              multi_class='multinomial'
    #                              ).fit(X,y)

    #     return str(clf.predict(X[:2,:]))

    return app


# def insert_users(usernames):
#     for id_index, username in enumerate(usernames):
#         user = User(id=id_index, username=username)
#         DB.session.add(user)
#         DB.session.commit()