import requests
from web3 import Web3
import yaml
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from config.yaml
with open("config/config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Etherscan and Web3 setup
ETHERSCAN_API_KEY = config['etherscan']['api_key']
WEB3_INFURA_URL = config['web3']['infura_url']
WALLET_ADDRESSES_TO_TRACK = config['web3']['wallet_addresses_to_track']

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(WEB3_INFURA_URL))

# Check if Web3 is connected
if not web3.isConnected():
    logging.error("Failed to connect to the Ethereum network. Check your Infura URL.")
else:
    logging.info("Connected to the Ethereum network successfully.")

# Function to get the balance of a wallet address
def get_wallet_balance(address):
    try:
        balance_wei = web3.eth.get_balance(address)
        balance_eth = web3.fromWei(balance_wei, 'ether')
        logging.info(f"Wallet Address: {address} | Balance: {balance_eth} ETH")
        return balance_eth
    except Exception as e:
        logging.error(f"Error fetching balance for {address}: {e}")
        return None

# Function to get the latest transactions of a wallet using Etherscan API
def get_wallet_transactions(address):
    try:
        url = f"https://api.etherscan.io/api"
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'desc',
            'apikey': ETHERSCAN_API_KEY
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            transactions = response.json().get("result", [])
            logging.info(f"Fetched {len(transactions)} transactions for {address}.")
            return transactions
        else:
            logging.warning(f"Error fetching transactions: {response.status_code}")
            return []
    except Exception as e:
        logging.error(f"Error in getting transactions for {address}: {e}")
        return []

# Monitor specified wallet addresses
for category, addresses in WALLET_ADDRESSES_TO_TRACK.items():
    logging.info(f"\nMonitoring {category}:")
    for wallet in addresses:
        balance = get_wallet_balance(wallet)
        transactions = get_wallet_transactions(wallet)
        # You can add more logic here to analyze or react to the transactions
