import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import backtrader as bt
import pandas as pd
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy

class PandasDataWithSentiment(bt.feeds.PandasData):
    lines = ('sentiment',)
    params = (('sentiment', -1),)

# Define a strategy that incorporates sentiment into trading decisions
class SentimentStrategy(bt.Strategy):
    params = dict(
        sentiment_threshold=0.1,
        take_profit=0.05,
        stop_loss=0.02
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.sentiment = self.datas[0].sentiment
        self.buy_price = None

    def next(self):
        if self.sentiment[0] != 0:
            print(f"Close: {self.dataclose[0]}, Sentiment: {self.sentiment[0]}")

        if not self.position and self.sentiment[0] > self.params.sentiment_threshold:

            self.buy()
            self.buy_price = self.dataclose[0]
            print(f"Buying at {self.dataclose[0]} with sentiment {self.sentiment[0]}")

        elif self.position:
            if self.dataclose[0] >= self.buy_price * (1 + self.params.take_profit):
                self.sell()
                print(f"Take-profit reached. Selling at {self.dataclose[0]}")

            elif self.dataclose[0] <= self.buy_price * (1 - self.params.stop_loss):
                self.sell()
                print(f"Stop-loss triggered. Selling at {self.dataclose[0]}")

            elif self.sentiment[0] <= -self.params.sentiment_threshold:
                self.sell()
                print(f"Selling at {self.dataclose[0]} with sentiment {self.sentiment[0]}")


def run_backtest_with_sentiment(strategy, data_df, name=""):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)

    # Add the data feed
    data = PandasDataWithSentiment(dataname=data_df)
    cerebro.adddata(data)

    # Set initial capital
    cerebro.broker.setcash(10000.0)

    # Run backtest
    print(f"\nRunning backtest for {name} with {strategy.__name__} strategy and sentiment.")
    cerebro.run()

    final_value = cerebro.broker.getvalue()
    print(f"Final Portfolio Value for {name} ({strategy.__name__}): ${final_value:.2f}")

# Load BTC/USD data and ensure proper datetime format
btc_data = pd.read_csv('data/crypto/BTC_USD_data.csv', parse_dates=['timestamp '])
btc_data.columns = btc_data.columns.str.strip()
btc_data['timestamp'] = pd.to_datetime(btc_data['timestamp'])
btc_data['date'] = btc_data['timestamp'].dt.date
btc_data['date'] = pd.to_datetime(btc_data['date'])

sentiment_data = pd.read_csv('data/sentiment/BTC_sentiment.csv', parse_dates=['date      '])
sentiment_data.columns = sentiment_data.columns.str.strip()
sentiment_data['date'] = pd.to_datetime(sentiment_data['date'])


merged_data = pd.merge(btc_data, sentiment_data, on='date', how='left')
merged_data = merged_data.assign(sentiment=merged_data['sentiment'].fillna(0))

# Run the backtest with the SentimentStrategy

merged_data.set_index('timestamp', inplace=True)

run_backtest_with_sentiment(SentimentStrategy, merged_data, "BTC/USD - Sentiment Based")
