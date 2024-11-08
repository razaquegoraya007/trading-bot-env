import praw
from transformers import pipeline
import requests
import yaml
import os
import time
import torch

# Load configuration from config.yaml
config_path = os.path.join(os.path.dirname(__file__), '../../config/config.yaml')

with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# Check for GPU and set the device
device = 0 if torch.cuda.is_available() else -1
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
sentiment_pipeline = pipeline("sentiment-analysis", model=model_name, device=device)

# Reddit API Setup
def setup_reddit_api():
    try:
        return praw.Reddit(
            client_id=config['reddit']['client_id'],
            client_secret=config['reddit']['client_secret'],
            user_agent=config['reddit']['user_agent']
        )
    except Exception as e:
        print(f"Error setting up Reddit API: {e}")
        return None

# News API Setup
def fetch_news_sentiment(retries=3):
    url = f"https://newsapi.org/v2/everything?q=cryptocurrency&apiKey={config['newsapi']['api_key']}"
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                articles = response.json().get("articles", [])
                sentiments = [sentiment_pipeline(article["title"])[0] for article in articles]
                return sentiments
            else:
                print(f"Error fetching news data (status code {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news data: {e}")
            time.sleep(5)  # Wait before retrying
    return []

# Analyze Reddit Sentiment
def analyze_reddit_sentiment(reddit, subreddit_name, limit=50):
    if not reddit:
        print("Reddit API not available.")
        print("Please check your Reddit API credentials in config.yaml.")
        return []
    try:
        subreddit = reddit.subreddit(subreddit_name)
        sentiments = [
            sentiment_pipeline(submission.title)[0] for submission in subreddit.hot(limit=limit)
        ]
        return sentiments
    except Exception as e:
        print(f"Error fetching Reddit data: {e}")
        return []

# Main Function to Aggregate Sentiment
def get_overall_sentiment():
    reddit_api = setup_reddit_api()

    reddit_sentiment = analyze_reddit_sentiment(reddit_api, "cryptocurrency")
    news_sentiment = fetch_news_sentiment()

    all_sentiments = reddit_sentiment + news_sentiment
    if not all_sentiments:
        print("No sentiment data collected.")
        return 0

    # Calculate average sentiment score
    sentiment_scores = [1 if s['label'] == 'POSITIVE' else -1 for s in all_sentiments]
    overall_sentiment = sum(sentiment_scores) / len(sentiment_scores)

    return overall_sentiment

if __name__ == "__main__":
    overall_sentiment_score = get_overall_sentiment()
    print(f"Overall Sentiment Score: {overall_sentiment_score}")
