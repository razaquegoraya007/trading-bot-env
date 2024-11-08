# src/strategies/mean_reversion.py

import backtrader as bt

class MeanReversionStrategy(bt.Strategy):
    params = dict(
        period=10,               # Shorter moving average period to capture shorter-term trends
        dev_threshold=0.5,       # Reduced threshold to trigger trades more easily
        stop_loss=0.02,          # Stop loss percentage (2%)
        take_profit=0.04         # Take profit percentage (4%)
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buy_price = None

        # Calculate moving average and standard deviation
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period)
        self.stdev = bt.indicators.StandardDeviation(self.data.close, period=self.params.period)

    def next(self):
        # Print statements for debugging each step's values
        print(f"Close: {self.dataclose[0]}, SMA: {self.sma[0]}, StdDev: {self.stdev[0]}")

        if self.order:
            return  # Skip if an order is pending

        if not self.position:
            # Buy if the price is lower than the moving average (a basic mean reversion condition)
            if self.dataclose[0] < self.sma[0]:
                self.buy_price = self.dataclose[0]
                self.order = self.buy()
                print(f"Buying at {self.dataclose[0]} (Mean: {self.sma[0]})")

        else:
            # Simple exit conditions based on stop loss and take profit
            stop_loss_price = self.buy_price * (1 - self.params.stop_loss)
            take_profit_price = self.buy_price * (1 + self.params.take_profit)

            # Stop Loss
            if self.dataclose[0] <= stop_loss_price:
                self.order = self.sell()
                print(f"Stop Loss hit. Selling at {self.dataclose[0]}")

            # Take Profit
            elif self.dataclose[0] >= take_profit_price:
                self.order = self.sell()
                print(f"Take Profit hit. Selling at {self.dataclose[0]}")

