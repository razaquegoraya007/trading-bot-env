import os
import yaml
from alpaca_trade_api.rest import REST, TimeFrame
import pandas as pd

# Load API keys from config
with open("config/config.yaml", 'r') as f:
    config = yaml.safe_load(f)

ALPACA_API_KEY = config['alpaca']['api_key']
ALPACA_SECRET_KEY = config['alpaca']['secret_key']

# Initialize Alpaca API
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url='https://paper-api.alpaca.markets')

def fetch_stock_data(symbol, start_date, end_date):
    """
    Fetches historical stock data using Alpaca.

    :param symbol: The stock symbol (e.g., 'AAPL')
    :param start_date: Start date for fetching data (format: 'YYYY-MM-DD')
    :param end_date: End date for fetching data (format: 'YYYY-MM-DD')
    """
    # Fetch historical bars using the new method
    bars = api.get_bars(symbol, TimeFrame.Day, start=start_date, end=end_date).df
    

    # Save the data
    bars.to_csv(f"data/stocks/{symbol}_data.csv")
    print(f"Data for {symbol} saved!")


# Example usage
if __name__ == '__main__':
    fetch_stock_data('AAPL', '2022-01-01', '2023-01-01')
