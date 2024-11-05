import backtrader as bt

class MomentumStrategy(bt.Strategy):
    params = dict(
        rsi_period=8,                  # Shorter period for more sensitivity
        rsi_overbought=65,             # Lowered to trigger more sell signals
        rsi_oversold=35,               # Raised to trigger more buy signals
        stop_loss=0.01,                # Stop-loss tightened to 1%
        take_profit=0.02               # Take-profit set at 2%
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.buy_price = None

    def next(self):
        # Print for debugging to ensure conditions are being checked
        print(f"Close: {self.data.close[0]}, RSI: {self.rsi[0]}")

        if self.position:
            # Stop-loss and take-profit conditions if in position
            if self.buy_price is not None:
                stop_loss_price = (1 - self.params.stop_loss) * self.buy_price
                take_profit_price = (1 + self.params.take_profit) * self.buy_price

                if self.data.close[0] <= stop_loss_price:
                    print(f"Stop-loss triggered. Selling at {self.data.close[0]}")
                    self.sell()
                    self.buy_price = None

                elif self.data.close[0] >= take_profit_price:
                    print(f"Take-profit reached. Selling at {self.data.close[0]}")
                    self.sell()
                    self.buy_price = None

        else:
            # Buy signal if RSI is below the oversold threshold
            if self.rsi[0] < self.params.rsi_oversold:
                self.buy()
                self.buy_price = self.data.close[0]
                print(f"Buying at {self.data.close[0]} (RSI oversold)")

            # Sell signal if RSI is above the overbought threshold
            elif self.rsi[0] > self.params.rsi_overbought:
                self.sell()
                print(f"Selling at {self.data.close[0]} (RSI overbought)")
