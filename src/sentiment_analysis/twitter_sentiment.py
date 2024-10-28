import tweepy
from textblob import TextBlob
import yaml
import time

# Load Twitter API credentials from config file
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

api_key = config['twitter']['api_key']
api_secret = config['twitter']['api_secret']
access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']

# Authenticate with Twitter
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, timeout=120)

# Function to fetch and analyze tweets with retries
def fetch_twitter_sentiment(keyword, tweet_count=100, retries=1):
    for attempt in range(retries):
        try:
            print(f"Attempt {attempt+1}/{retries}...")
            # Fetch tweets with the specified keyword
            tweets = api.search_tweets(q=keyword, count=tweet_count, lang='en')
            print(f"Fetched {len(tweets)} tweets.")
            sentiments = []

            for tweet in tweets:
                analysis = TextBlob(tweet.text)
                sentiment = analysis.sentiment.polarity  # Get polarity for sentiment score (-1 to 1)
                sentiments.append(sentiment)
                print(f"Tweet: {tweet.text}\nSentiment Score: {sentiment}\n")

            # Calculate average sentiment
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            print(f"\nAverage Sentiment for '{keyword}': {avg_sentiment}")
            return avg_sentiment

        except tweepy.errors.TooManyRequests as e:
            print("Rate limit exceeded. Retrying in 15 minutes...")
            time.sleep(900)  # Wait 15 minutes and try again if rate limit exceeded

        except tweepy.errors.TweepyException as e:
            print(f"Error: {e}. Retrying in 10 seconds...")
            time.sleep(10)

    print("Max retries exceeded. Could not fetch tweets.")
    return None

if __name__ == "__main__":
    fetch_twitter_sentiment("Bitcoin", tweet_count=10)
