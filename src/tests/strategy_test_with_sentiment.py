import sys
import os
import backtrader as bt
import pandas as pd
from praw import Reddit
from textblob import TextBlob
import yaml

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Load configuration
with open("config/config.yaml", 'r') as file:
    config = yaml.safe_load(file)

# Set up Reddit API
reddit = Reddit(
    client_id=config['reddit']['client_id'],
    client_secret=config['reddit']['client_secret'],
    user_agent="trading_bot"
)

class PandasDataWithSentiment(bt.feeds.PandasData):
    lines = ('sentiment',)
    params = (('sentiment', -1),)

# Define a strategy that incorporates combined sentiment into trading decisions
class SentimentStrategy(bt.Strategy):
    params = dict(
        sentiment_threshold=0.1,
        take_profit=0.05,
        stop_loss=0.02,
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.sentiment = self.datas[0].sentiment
        self.buy_price = None

    def next(self):
        if self.sentiment[0] != 0:
            print(f"Close: {self.dataclose[0]}, Combined Sentiment: {self.sentiment[0]}")

        if not self.position and self.sentiment[0] > self.params.sentiment_threshold:
            self.buy()
            self.buy_price = self.dataclose[0]
            print(f"Buying at {self.dataclose[0]} with sentiment {self.sentiment[0]}")

        elif self.position:
            if self.datacose[0] >= self.buy_price * (1 + self.params.take_profit):
                self.sell()
                print(f"Take-profit reached. Selling at {self.dataclose[0]}")

            elif self.dataclose[0] <= self.buy_price * (1 - self.params.stop_loss):
                self.sell()
                print(f"Stop-loss triggered. Selling at {self.dataclose[0]}")


            elif self.sentiment[0] <= -self.params.sentiment_threshold:
                self.sell()
                print(f"Selling at {self.dataclose[0]} with sentiment {self.sentiment[0]}")

def fetch_reddit_sentiment(subreddit_name="CryptoCurrency", post_limit=10):
    subreddit = reddit.subreddit(subreddit_name)
    posts = subreddit.hot(limit=post_limit)

    sentiments = []
    for post in posts:
        analysis = TextBlob(post.title)
        sentiments.append(analysis.sentiment.polarity)

    return sum(sentiments) / len(sentiments) if sentiments else 0

# Function to run backtest with combined sentiment
def run_backtest_with_sentiment(strategy, data_df, name=""):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)

    # Fetch Reddit sentiment and integrate it
    reddit_sentiment = fetch_reddit_sentiment()
    data_df['combined_sentiment'] = (data_df['sentiment'] + reddit_sentiment) / 2

    data = PandasDataWithSentiment(dataname=data_df, sentiment='combined_sentiment')
    cerebro.adddata(data)

    cerebro.broker.setcash(10000.0)

    print(f"\nRunning backtest for {name} with {strategy.__name__} strategy and combined sentiment.")
    cerebro.run()

    final_value = cerebro.broker.getvalue()
    print(f"Final Portfolio Value for {name} ({strategy.__name__}): ${final_value:.2f}")



btc_data = pd.read_csv('data/crypto/BTC_USD_data.csv', parse_dates=['timestamp '])
btc_data.columns = btc_data.columns.str.strip()
btc_data['date'] = pd.to_datetime(btc_data['timestamp']).dt.date

sentiment_data = pd.read_csv('data/sentiment/BTC_sentiment.csv', parse_dates=['date      '])
sentiment_data.columns = sentiment_data.columns.str.strip()
sentiment_data['date'] = pd.to_datetime(sentiment_data['date']).dt.date

merged_data = pd.merge(btc_data, sentiment_data, on='date', how='left')
merged_data = merged_data.assign(sentiment=merged_data['sentiment'].fillna(0))


merged_data.set_index('timestamp', inplace=True)
run_backtest_with_sentiment(SentimentStrategy, merged_data, "BTC/USD - Sentiment Enhanced")