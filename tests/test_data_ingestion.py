import unittest
from src.data_ingestion.crypto_kraken import fetch_crypto_data

class TestDataIngestion(unittest.TestCase):

    def test_fetch_crypto_data(self):
        try:
            fetch_crypto_data('BTC/USD')
            self.assertTrue(True)  # If no exception, pass the test
        except Exception as e:
            self.fail(f"Data ingestion failed: {e}")

if __name__ == '__main__':
    unittest.main()
