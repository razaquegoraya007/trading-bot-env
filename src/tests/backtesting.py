import backtrader as bt
import pandas as pd
import sys
import os
import matplotlib.pyplot as plt

# Add the root project directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import the sentiment analysis function
from src.utils.sentiment_analysis import get_overall_sentiment

class CustomPandasData(bt.feeds.PandasData):
    params = (
        ('datetime', None),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
    )

class EnhancedStrategy(bt.Strategy):
    params = dict(
        rsi_period=14,
        rsi_upper=70,  # Adjusted to be more selective
        rsi_lower=30,  # Adjusted to be more selective
        atr_period=14,
        atr_multiplier=1.0,  # Adjusted for better stop-loss/take-profit levels
        sentiment_threshold=-0.2  # New parameter for sentiment filtering
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buy_price = None
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data.close, period=self.params.rsi_period)
        self.atr = bt.indicators.AverageTrueRange(self.data, period=self.params.atr_period)
        self.trade_log = []

        # Fetch overall sentiment score
        self.overall_sentiment = get_overall_sentiment()
        print(f"Initial Overall Sentiment Score: {self.overall_sentiment}")

    def log(self, text):
        """ Logging function for this strategy """
        print(f'{self.data.datetime.date(0)}: {text}')

    def next(self):
        # Log RSI and Close price for each bar
        self.log(f'RSI: {self.rsi[0]}, Close: {self.dataclose[0]}')

        if self.order:
            return  # Skip if there's a pending order

        if not self.position:
            # Buy condition: RSI below lower threshold and positive sentiment score
            if self.rsi[0] < self.params.rsi_lower and self.overall_sentiment > self.params.sentiment_threshold:
                self.buy_price = self.dataclose[0]
                self.order = self.buy()
                self.trade_log.append(f"BUY at {self.dataclose[0]} with RSI {self.rsi[0]}")
                self.log(f"BUY at {self.dataclose[0]} with RSI {self.rsi[0]}")
        else:
            # Dynamic stop-loss and take-profit based on ATR
            stop_loss_price = self.buy_price - (self.params.atr_multiplier * self.atr[0])
            take_profit_price = self.buy_price + (self.params.atr_multiplier * self.atr[0])

            # Sell conditions: Stop-loss, Take-profit, or RSI above upper threshold
            if self.dataclose[0] <= stop_loss_price:
                self.order = self.sell()
                self.trade_log.append(f"SELL (Stop Loss) at {self.dataclose[0]} with RSI {self.rsi[0]}")
                self.log(f"SELL (Stop Loss) at {self.dataclose[0]} with RSI {self.rsi[0]}")
                self.buy_price = None

            elif self.dataclose[0] >= take_profit_price or self.rsi[0] > self.params.rsi_upper:
                self.order = self.sell()
                self.trade_log.append(f"SELL (Take Profit or RSI Overbought) at {self.dataclose[0]} with RSI {self.rsi[0]}")
                self.log(f"SELL (Take Profit or RSI Overbought) at {self.dataclose[0]} with RSI {self.rsi[0]}")
                self.buy_price = None

    def stop(self):
        # Ensure any open position is closed at the end of the backtest
        if self.position:
            self.order = self.sell()
            self.trade_log.append(f"FORCED SELL at {self.dataclose[0]} (End of Backtest)")
            self.log(f"FORCED SELL at {self.dataclose[0]} (End of Backtest)")

# Function to load CSV data
def load_data(filepath, date_column='timestamp'):
    try:
        data = pd.read_csv(filepath, sep=';', engine='python')
        data.columns = data.columns.str.strip()
        date_column = next((col for col in data.columns if 'timestamp' in col.lower()), date_column)

        data[date_column] = pd.to_datetime(data[date_column], errors='coerce')
        data.dropna(subset=[date_column], inplace=True)
        data.set_index(date_column, inplace=True)

        column_mapping = {
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume'
        }
        data.rename(columns=column_mapping, inplace=True)

        return data[['open', 'high', 'low', 'close', 'volume']]
    except ValueError as e:
        print(f"Error: {e}")
        print(f"Available columns in {filepath}: {pd.read_csv(filepath, sep=';', engine='python').columns}")
        return None

# Function to run backtests
def run_backtest_with_metrics(data, condition_name, figure_number):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(EnhancedStrategy)
    data_feed = CustomPandasData(dataname=data)
    cerebro.adddata(data_feed, name=condition_name)

    cerebro.broker.setcash(10000.0)

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    print(f"\nRunning backtest for {condition_name} market condition.")
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()
    print(f"Ending Portfolio Value for {condition_name}: {final_value:.2f}")

    sharpe_ratio = results[0].analyzers.sharpe.get_analysis().get('sharperatio', 'N/A')
    drawdown = results[0].analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 'N/A')
    trade_analysis = results[0].analyzers.trades.get_analysis()

    total_closed = trade_analysis.total.closed if 'total' in trade_analysis and 'closed' in trade_analysis.total else 0
    won_trades = trade_analysis.won.total if 'won' in trade_analysis and 'total' in trade_analysis.won else 0
    pnl_won = trade_analysis.won.pnl.total if 'won' in trade_analysis and 'pnl' in trade_analysis.won else 0
    pnl_lost = trade_analysis.lost.pnl.total if 'lost' in trade_analysis and 'pnl' in trade_analysis.lost else 0

    win_rate = (won_trades / total_closed) * 100 if total_closed > 0 else 0
    profit_factor = (pnl_won / abs(pnl_lost)) if pnl_lost != 0 else float('inf')

    print(f"\nTrade Log:")
    for entry in results[0].trade_log:
        print(entry)

    print(f"\nMetrics Summary for {condition_name}:")
    print("Sharpe Ratio:", sharpe_ratio)
    print("Max Drawdown:", drawdown)
    print("Win Rate: {:.2f}%".format(win_rate))
    print("Profit Factor:", profit_factor)

    # Save the plot for the market condition
    cerebro.plot(figure=figure_number)

# Market conditions
market_conditions = {
    'Bull Market': 'data/bull_market.csv',
    'Bear Market': 'data/bear_market.csv',
    'Sideways Market': 'data/sideways_market.csv'
}

# Create a figure for plotting
plt.figure(figsize=(15, 10))

# Run backtests for each market condition and plot on the same figure
for i, (condition_name, file_path) in enumerate(market_conditions.items(), start=1):
    market_data = load_data(file_path)
    if market_data is not None:
        run_backtest_with_metrics(market_data, condition_name, figure_number=i)
    else:
        print(f"Failed to load data for {condition_name}.")

# Show all plots together
plt.show()
