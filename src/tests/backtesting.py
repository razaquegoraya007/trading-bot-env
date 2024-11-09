import backtrader as bt
import pandas as pd
import sys
import os
import logging

# Reduce logging verbosity from matplotlib
logging.getLogger('matplotlib').setLevel(logging.WARNING)

# Add the project root directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import utility functions
from src.utils.sentiment_analysis import get_overall_sentiment
from src.utils.defi_integration import check_yield_and_reinvest

# Custom data feed class for Backtrader using Pandas data
class CustomPandasData(bt.feeds.PandasData):
    params = (
        ('datetime', None),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
    )

# Define the trading strategy
class EnhancedStrategy(bt.Strategy):
    params = dict(
        rsi_period=14,
        rsi_upper=70,
        rsi_lower=30,
        atr_period=14,
        atr_multiplier=1.0,
        sentiment_threshold=-0.2,
        reinvest_threshold=100
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buy_price = None
        self.rsi = bt.indicators.RelativeStrengthIndex(self.data.close, period=self.params.rsi_period)
        self.atr = bt.indicators.AverageTrueRange(self.data, period=self.params.atr_period)
        self.trade_log = []
        self.overall_sentiment = get_overall_sentiment()
        self.cumulative_profit = 0
        logging.debug("Strategy initialized with parameters: %s", self.params)

    def log(self, text):
        logging.info(f'{self.data.datetime.date(0)}: {text}')

    def next(self):
        self.log(f'RSI: {self.rsi[0]}, Close: {self.dataclose[0]}, Sentiment: {self.overall_sentiment}')
        logging.debug("Next step - Close: %.2f, RSI: %.2f, Sentiment: %.2f", self.dataclose[0], self.rsi[0], self.overall_sentiment)

        if self.order:
            logging.debug("Order already placed, skipping iteration.")
            return

        # Check if there is an open position
        if not self.position:
            if self.rsi[0] < self.params.rsi_lower and self.overall_sentiment > self.params.sentiment_threshold:
                self.buy_price = self.dataclose[0]
                self.order = self.buy()
                self.log(f"BUY at {self.dataclose[0]} with RSI {self.rsi[0]}")
                logging.debug("BUY order placed at %.2f", self.dataclose[0])
        else:
            # Calculate stop loss and take profit
            stop_loss_price = self.buy_price - (self.params.atr_multiplier * self.atr[0])
            take_profit_price = self.buy_price + (self.params.atr_multiplier * self.atr[0])

            logging.debug("Stop Loss: %.2f, Take Profit: %.2f", stop_loss_price, take_profit_price)

            # Check if we should sell
            if self.dataclose[0] <= stop_loss_price:
                self.order = self.sell()
                self.log(f"SELL (Stop Loss) at {self.dataclose[0]} with RSI {self.rsi[0]}")
                logging.debug("Stop loss triggered, SELL order placed at %.2f", self.dataclose[0])
                self.cumulative_profit += self.dataclose[0] - self.buy_price
                self.buy_price = None
            elif self.dataclose[0] >= take_profit_price or self.rsi[0] > self.params.rsi_upper:
                self.order = self.sell()
                self.log(f"SELL (Take Profit or RSI Overbought) at {self.dataclose[0]} with RSI {self.rsi[0]}")
                logging.debug("Take profit or RSI overbought, SELL order placed at %.2f", self.dataclose[0])
                self.cumulative_profit += self.dataclose[0] - self.buy_price
                self.buy_price = None

            # Check for reinvestment
            if self.cumulative_profit >= self.params.reinvest_threshold:
                check_yield_and_reinvest()
                self.log(f"Profit Reinvestment triggered (Cumulative Profit: {self.cumulative_profit:.2f})")
                logging.debug("Reinvesting profits, cumulative profit reset.")
                self.cumulative_profit = 0

    def stop(self):
        if self.position:
            self.order = self.sell()
            self.log(f"FORCED SELL at {self.dataclose[0]} (End of Backtest)")
            logging.debug("Forced SELL at %.2f due to end of backtest", self.dataclose[0])

# Function to load CSV data
def load_data(filepath, date_column='timestamp'):
    try:
        logging.debug("Loading data from %s", filepath)
        data = pd.read_csv(filepath, sep=';', engine='python')
        data.columns = data.columns.str.strip()
        date_column = next((col for col in data.columns if 'timestamp' in col.lower()), date_column)
        data[date_column] = pd.to_datetime(data[date_column], errors='coerce')
        data.dropna(subset=[date_column], inplace=True)
        data.set_index(date_column, inplace=True)
        column_mapping = {'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close', 'volume': 'volume'}
        data.rename(columns=column_mapping, inplace=True)
        logging.debug("Data loaded successfully with columns: %s", data.columns)
        return data[['open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        logging.error("Error loading data: %s", e)
        print(f"Error: {e}")
        return None

# Function to run backtests with detailed metrics
def run_backtest_with_metrics(data, condition_name):
    cerebro = bt.Cerebro()
    cerebro.addstrategy(EnhancedStrategy)
    data_feed = CustomPandasData(dataname=data)
    cerebro.adddata(data_feed, name=condition_name)
    cerebro.broker.setcash(10000.0)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')

    logging.info(f"Running backtest for {condition_name} market condition.")
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()
    logging.info(f"Ending Portfolio Value for {condition_name}: {final_value:.2f}")

    # Extract metrics
    sharpe_ratio = results[0].analyzers.sharpe.get_analysis().get('sharperatio', 'N/A')
    drawdown = results[0].analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 'N/A')
    trade_analysis = results[0].analyzers.trades.get_analysis()

    total_closed = trade_analysis.total.closed if 'total' in trade_analysis and 'closed' in trade_analysis.total else 0
    won_trades = trade_analysis.won.total if 'won' in trade_analysis and 'total' in trade_analysis.won else 0
    pnl_won = trade_analysis.won.pnl.total if 'won' in trade_analysis and 'pnl' in trade_analysis.won else 0
    pnl_lost = trade_analysis.lost.pnl.total if 'lost' in trade_analysis and 'pnl' in trade_analysis.lost else 0

    # Calculate win rate and profit factor
    win_rate = (won_trades / total_closed) * 100 if total_closed > 0 else 0
    profit_factor = (pnl_won / abs(pnl_lost)) if pnl_lost != 0 else float('inf')

    # Output metrics
    logging.info(f"Metrics Summary for {condition_name}:")
    logging.info("Sharpe Ratio: %s", sharpe_ratio)
    logging.info("Max Drawdown: %s", drawdown)
    logging.info("Win Rate: %.2f%%", win_rate)
    logging.info("Profit Factor: %s", profit_factor)

    # Plot backtest results
    cerebro.plot()

# Main execution
if __name__ == "__main__":
    market_conditions = {
        'Bull Market': 'data/bull_market.csv',
        'Bear Market': 'data/bear_market.csv',
        'Sideways Market': 'data/sideways_market.csv'
    }

    for condition_name, file_path in market_conditions.items():
        market_data = load_data(file_path)
        if market_data is not None:
            run_backtest_with_metrics(market_data, condition_name)
        else:
            logging.error(f"Failed to load data for {condition_name}.")
