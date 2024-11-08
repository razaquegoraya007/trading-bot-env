import praw
from transformers import pipeline
import requests
import yaml
import os
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from config.yaml
config_path = os.path.join(os.path.dirname(__file__), '../../config/config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# Setup Reddit API
def setup_reddit_api():
    try:
        reddit = praw.Reddit(
            client_id=config['reddit']['client_id'],
            client_secret=config['reddit']['client_secret'],
            user_agent=config['reddit']['user_agent']
        )
        logging.debug("Reddit API setup successful.")
        return reddit
    except Exception as e:
        logging.error(f"Error setting up Reddit API: {e}")
        return None

# News API Setup
def fetch_news_sentiment():
    try:
        url = f"https://newsapi.org/v2/everything?q=cryptocurrency&apiKey={config['newsapi']['api_key']}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            logging.debug(f"Fetched {len(articles)} articles from News API.")
            sentiments = [sentiment_pipeline(article["title"])[0] for article in articles if article.get("title")]
            return sentiments
        else:
            logging.error(f"Error fetching news data: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching news data: {e}")
        return []

# Hugging Face Sentiment Analysis
sentiment_pipeline = pipeline("sentiment-analysis", device=-1)  # Use CPU (-1) or GPU (0) if available

# Analyze Reddit Sentiment
def analyze_reddit_sentiment(reddit, subreddit_name, limit=100):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        sentiments = [
            sentiment_pipeline(submission.title)[0] for submission in subreddit.hot(limit=limit)
            if submission.title
        ]
        logging.debug(f"Fetched {len(sentiments)} sentiments from Reddit.")
        return sentiments
    except Exception as e:
        logging.error(f"Error fetching Reddit data: {e}")
        return []

# Main Function to Aggregate Sentiment
def get_overall_sentiment():
    reddit_api = setup_reddit_api()
    if not reddit_api:
        logging.error("Reddit API not available.")
        return 0

    reddit_sentiment = analyze_reddit_sentiment(reddit_api, "cryptocurrency")
    news_sentiment = fetch_news_sentiment()

    all_sentiments = reddit_sentiment + news_sentiment
    if not all_sentiments:
        logging.warning("No sentiment data collected.")
        return 0

    # Fine-tuned sentiment score calculation
    sentiment_scores = []
    for sentiment in all_sentiments:
        if sentiment['label'] == 'POSITIVE':
            sentiment_scores.append(1 * sentiment['score'])  # Weigh positive sentiments by their score
        elif sentiment['label'] == 'NEGATIVE':
            sentiment_scores.append(-1 * sentiment['score'])  # Weigh negative sentiments by their score

    overall_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    logging.debug(f"Overall sentiment score: {overall_sentiment}")
    return overall_sentiment

if __name__ == "__main__":
    overall_sentiment_score = get_overall_sentiment()
    print(f"Overall Sentiment Score: {overall_sentiment_score}")
