import ccxt
import yaml
import pandas as pd

# Load API keys from config
with open("config/config.yaml", 'r') as f:
    config = yaml.safe_load(f)

KRAKEN_API_KEY = config['kraken']['api_key']
KRAKEN_SECRET_KEY = config['kraken']['secret_key']

# Initialize Kraken API
kraken = ccxt.kraken({
    'apiKey': KRAKEN_API_KEY,
    'secret': KRAKEN_SECRET_KEY,
})

def fetch_crypto_data(symbol):
    """
    Fetches OHLCV data for a given cryptocurrency pair from Kraken.

    :param symbol: The trading pair symbol (e.g., 'BTC/USD')
    """
    try:
        # Fetch OHLCV data from Kraken (1-day candles)
        ohlcv = kraken.fetch_ohlcv(symbol, timeframe='1d')

        # Convert to a DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Save to CSV
        df.to_csv(f"data/crypto/{symbol.replace('/', '_')}_data.csv", index=False)
        print(f"Crypto data for {symbol} saved to data/crypto/")

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")

# Example usage
if __name__ == '__main__':
    fetch_crypto_data('BTC/USD')
