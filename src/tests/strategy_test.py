import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import backtrader as bt
import pandas as pd
from strategies.mean_reversion import MeanReversionStrategy
from strategies.momentum import MomentumStrategy

# Define custom data feed for Backtrader compatibility
class PandasData(bt.feeds.PandasData):
    params = (('datetime', None), ('open', 'open'), ('high', 'high'), ('low', 'low'), ('close', 'close'), ('volume', 'volume'), ('openinterest', None))

# Function to run backtest for each strategy and dataset
def run_backtest(strategy, data_df, name=""):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)

    # Add the data feed
    data = PandasData(dataname=data_df)
    cerebro.adddata(data)

    # Set initial capital
    cerebro.broker.setcash(10000.0)

    # Run backtest
    print(f"\nRunning backtest for {name} with {strategy.__name__} strategy.")
    cerebro.run()

    # Get final portfolio value
    final_value = cerebro.broker.getvalue()
    print(f"Final Portfolio Value for {name} ({strategy.__name__}): ${final_value:.2f}")

# Load BTC/USD data and clean the column names
btc_data = pd.read_csv('data/crypto/BTC_USD_data.csv', parse_dates=['timestamp '])
btc_data.columns = btc_data.columns.str.strip()  # Strip extra spaces
btc_data.set_index('timestamp', inplace=True)

aapl_data = pd.read_csv('data/stocks/AAPL_data.csv', parse_dates=['timestamp                '])
aapl_data.columns = aapl_data.columns.str.strip()  # Strip extra spaces
aapl_data.set_index('timestamp', inplace=True)

# Run backtests without plotting
run_backtest(MeanReversionStrategy, btc_data, "BTC/USD - Mean Reversion")
run_backtest(MomentumStrategy, btc_data, "BTC/USD - Momentum")
run_backtest(MeanReversionStrategy, aapl_data, "AAPL - Mean Reversion")
run_backtest(MomentumStrategy, aapl_data, "AAPL - Momentum")
