"""Handles DS prediction model"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from .models import User
from .twitter import vectorize_tweet


def predict_user(user0_name, user1_name, hypo_tweet_text):
    """Determines which user is more likely to tweet a given hypothetical.

    Example run: predict_user ('elonmusk', 'jackblack', 'Doge to the moon!')
    Returns a 0 (user0_name) or a 1 (user1_name).
    """

    # Grab user names from SQLite Database through SQLAlchemy
    user0 = User.query.filter(User.username == user0_name).one()
    user1 = User.query.filter(User.username == user1_name).one()

    # Grab tweets from SQLite Database using SQLAlchemy per user
    user0_vects = np.array([tweet.vect for tweet in user0.tweets])
    user1_vects = np.array([tweet.vect for tweet in user1.tweets])

    # Vertically stack the vectors together (feature matrix (X))
    vects = np.vstack([user0_vects, user1_vects])

    # Create binary labels to be paired with vectors (labels are the target (y))
    labels = np.concatenate(
        [np.zeros(len(user0.tweets)), np.ones(len(user1.tweets))]
        )

    # Create and train a simple predictive model
    log_reg = LogisticRegression().fit(vects, labels)

    # Vectorize the hypothetical tweet and reshape it to be used in prediction
    hypo_tweet_vect = vectorize_tweet(hypo_tweet_text).reshape(1,-1)

    return log_reg.predict(hypo_tweet_vect)