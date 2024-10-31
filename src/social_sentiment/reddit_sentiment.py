import praw
from textblob import TextBlob
import yaml

# Load config
with open("config/config.yaml", 'r') as file:
    config = yaml.safe_load(file)

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=config['reddit']['client_id'],
    client_secret=config['reddit']['client_secret'],
    user_agent=config['reddit']['user_agent'],
    redirect_uri=config['reddit']['redirect_uri']
)

def fetch_reddit_sentiment(subreddit_name, limit=10):
    subreddit = reddit.subreddit(subreddit_name)
    sentiments = []

    for submission in subreddit.hot(limit=limit):
        analysis = TextBlob(submission.title)
        sentiment_score = analysis.sentiment.polarity
        sentiments.append(sentiment_score)
        print(f"Title: {submission.title}\nSentiment Score: {sentiment_score}\n")

    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    print(f"\nAverage Sentiment for r/{subreddit_name}: {avg_sentiment}")
    return avg_sentiment

fetch_reddit_sentiment("CryptoCurrency", limit=10)

