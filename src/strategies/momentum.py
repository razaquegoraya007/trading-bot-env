import backtrader as bt
class MomentumStrategy(bt.Strategy):
    params = dict(rsi_period=14, rsi_overbought=80, rsi_oversold=20, stop_loss=0.02, take_profit=0.05)

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.atr = bt.indicators.AverageTrueRange(self.data, period=14)  # ATR for volatility
        self.buy_price = None

    def next(self):
        if self.position:
            if self.buy_price is not None:
                # Stop-loss and take-profit conditions
                if self.data.close[0] < (1 - self.params.stop_loss) * self.buy_price:
                    print(f"Stop-loss triggered. Selling at {self.data.close[0]}")
                    self.sell()
                    self.buy_price = None

                elif self.data.close[0] > (1 + self.params.take_profit) * self.buy_price:
                    print(f"Take-profit reached. Selling at {self.data.close[0]}")
                    self.sell()
                    self.buy_price = None

        else:
            if self.rsi < self.params.rsi_oversold and self.atr[0] > 1:  # Buy if RSI is oversold and ATR is high
                self.buy()  # Buy signal
                self.buy_price = self.data.close[0]
                print(f"Buying at {self.data.close[0]} (RSI oversold, high volatility)")

            elif self.rsi > self.params.rsi_overbought:  # Sell if RSI is overbought
                self.sell()  # Sell signal
                print(f"Selling at {self.data.close[0]} (RSI overbought)")
