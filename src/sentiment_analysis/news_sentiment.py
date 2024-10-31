import requests
from textblob import TextBlob
import yaml

with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

api_key = config['newsapi']['api_key']


def fetch_news_sentiment(keyword, article_limit=10):
    url = f"https://newsapi.org/v2/everything?q={keyword}&language=en&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch articles. Status Code: {response.status_code}")
        return None

    data = response.json()
    articles = data.get('articles', [])

    if not articles:
        print(f"No articles found for keyword: {keyword}")
        return None

    sentiments = []
    for article in articles[:article_limit]:
        title = article.get('title', '')
        description = article.get('description', '')
        full_text = f"{title} {description}"
        analysis = TextBlob(full_text)
        sentiment = analysis.sentiment.polarity
        sentiments.append(sentiment)
        print(f"Article Title: {title}\nSentiment Score: {sentiment}\n")

    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    print(f"\nAverage Sentiment for '{keyword}' in News: {avg_sentiment}")
    return avg_sentiment

if __name__ == "__main__":
    fetch_news_sentiment("Bitcoin", article_limit=10)
