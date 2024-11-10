from web3 import Web3
import yaml

# Load API keys from config
with open("config/config.yaml", 'r') as f:
    config = yaml.safe_load(f)

INFURA_URL = config['web3']['infura_url']

# Initialize Web3 connection
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

def fetch_aave_data():
    """
    Fetches data from Aave protocol via Web3.
    """
    lending_pool_address = '0x398EC7346DcD622eDc5ae82352F02bE94C62d119'  # Aave Lending Pool address
    lending_pool = web3.eth.contract(address=lending_pool_address, abi=[])

    # Fetch data (specific methods depend on contract ABI)
    # Example: Get available liquidity or interest rates

    print("Data fetched from Aave")

# Example usage
if __name__ == '__main__':
    fetch_aave_data()
