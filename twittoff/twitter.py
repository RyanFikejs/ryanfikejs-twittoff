"""Handle connection to twitter database"""

from os import getenv
import tweepy
import spacy
from .models import DB, Tweet, User


TWITTER_API_KEY = getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = getenv("TWITTER_API_KEY_SECRET")
TWITTER_AUTH = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
api = tweepy.API(TWITTER_AUTH)


# Natural Language Processing Model
nlp = spacy.load("my_model")

# Create vectors from the text of a tweet
def vectorize_tweet(tweet_text):
    """Vectorizes the text using """
    return nlp(tweet_text).vector


def add_or_update_user(username):
    """Takes a username and adds them to our DB from the twitter DB
    
    Get user and get up to 200 of their tweets and add to our
    SQLAlchemy DB.    
    """

    try:
        # Decide whether to add or update id / username
        twitter_user = api.get_user(username)
        db_user = User.query.get(twitter_user.id) or User(
            id=twitter_user.id, username=username)

        DB.session.add(db_user)

        tweets = twitter_user.timeline(
            count=200,
            exclude_replies=True,
            include_rts=False,
            tweet_mode="extended",
            since_id=db_user.newest_tweet_id
        )

        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        for tweet in tweets:
            # Vectorize the text of the tweet
            db_vect = vectorize_tweet(tweet.full_text)
            # Define the info from the API that we want stored in our DB
            db_tweet = Tweet(id=tweet.id,
                             text=tweet.full_text,
                             vect=db_vect
                             )
            # Connects the tweet to user through this tweets list (user.tweets)
            db_user.tweets.append(db_tweet)
            # Note: if added before appending an error is likely
            DB.session.add(db_tweet)

    except Exception as e:
        print(f"Error processing {username}: {e}")
        raise e

    else:
        DB.session.commit()