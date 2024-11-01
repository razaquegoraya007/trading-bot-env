import backtrader as bt
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from datetime import datetime
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy

class CustomPandasData(bt.feeds.PandasData):
    params = (
        ('datetime', None),   # Backtrader will use the index as the datetime
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
    )

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.dataclose = self.datas[0].close

    def next(self):
        if not self.position:
            if self.dataclose[0] > self.dataclose[-1]:
                self.buy()
                print(f"Buying at {self.dataclose[0]}")
        else:
            if self.dataclose[0] < self.dataclose[-1]:
                self.sell()
                print(f"Selling at {self.dataclose[0]}")

# Load CSV data with flexible error handling
def load_data(filepath, date_column='timestamp'):
    try:
        data = pd.read_csv(filepath)
        data.columns = data.columns.str.strip()  # Strip extra spaces from column names
        data[date_column] = pd.to_datetime(data[date_column].str.strip())  # Ensure 'timestamp' is datetime
        data.set_index(date_column, inplace=True)
        return data
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Available columns in {filepath}: {pd.read_csv(filepath).columns}")
        return None

# Load data for stock and crypto
stock_data = load_data('data/stocks/AAPL_data.csv')
crypto_data = load_data('data/crypto/BTC_USD_data.csv')

if stock_data is not None and crypto_data is not None:
    # Set up Cerebro
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

    # Add data feeds
    data_stock = CustomPandasData(dataname=stock_data)
    cerebro.adddata(data_stock, name="AAPL Stock")

    data_crypto = CustomPandasData(dataname=crypto_data)
    cerebro.adddata(data_crypto, name="BTC Crypto")

    # Set initial cash
    cerebro.broker.setcash(10000.0)

    # Add performance analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    # Run backtest
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    results = cerebro.run()
    print("Ending Portfolio Value: %.2f" % cerebro.broker.getvalue())

    # Extract and print metrics
    sharpe_ratio = results[0].analyzers.sharpe.get_analysis().get('sharperatio', 'N/A')
    drawdown = results[0].analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 'N/A')
    trade_analysis = results[0].analyzers.trades.get_analysis()

    # Calculate Win Rate and Profit Factor
    win_rate = (trade_analysis.won.total / trade_analysis.total.closed) * 100 if trade_analysis.total.closed > 0 else 0
    profit_factor = (trade_analysis.won.pnl.total / abs(trade_analysis.lost.pnl.total)
                    if trade_analysis.lost.pnl.total != 0 else float('inf'))

    print("\nMetrics Summary:")
    print("Sharpe Ratio:", sharpe_ratio)
    print("Max Drawdown:", drawdown)
    print("Win Rate: {:.2f}%".format(win_rate))
    print("Profit Factor:", profit_factor)

    cerebro.plot()
else:
    print("Failed to load one or both of the data files.")
