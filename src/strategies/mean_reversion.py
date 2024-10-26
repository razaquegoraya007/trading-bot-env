import backtrader as bt
class MeanReversionStrategy(bt.Strategy):
    params = dict(sma_period=100, stop_loss=0.02, take_profit=0.05)  # Adjusted SMA period and stop-loss/take-profit

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_period)
        self.buy_price = None

    def next(self):
        if self.position:  # If the strategy is holding a position (i.e., already bought)
            if self.buy_price is not None:  # Only apply stop-loss/take-profit if we have a buy price
                # Calculate stop-loss and take-profit levels
                if (self.data.close[0] < (1 - self.params.stop_loss) * self.buy_price):
                    print(f"Stop-loss triggered. Selling at {self.data.close[0]}")
                    self.sell()  # Exit on stop-loss
                    self.buy_price = None  # Reset buy price after sell

                elif self.data.close[0] > (1 + self.params.take_profit) * self.buy_price:
                    print(f"Take-profit reached. Selling at {self.data.close[0]}")
                    self.sell()  # Exit on take-profit
                    self.buy_price = None  # Reset buy price after sell

        else:
            if self.data.close[0] < self.sma[0]:  # If price is below SMA, consider oversold
                self.buy()  # Buy signal
                self.buy_price = self.data.close[0]  # Set the buy price
                print(f"Buying at {self.data.close[0]} (below SMA)")

            elif self.data.close[0] > self.sma[0]:  # If price is above SMA
                self.sell()  # Sell signal
                print(f"Selling at {self.data.close[0]} (above SMA)")
