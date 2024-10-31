import json
import time
from web3 import Web3
import yaml
import os

# Load configuration
with open("config/config.yaml", 'r') as file:
    config = yaml.safe_load(file)

# Connect to Infura
web3 = Web3(Web3.HTTPProvider(config['web3']['infura_url']))

# Convert addresses to checksum format
aave_address = Web3.to_checksum_address(config['aave']['contract_address'])
compound_address = Web3.to_checksum_address(config['compound']['contract_address'])

# Load Aave and Compound ABIs
with open(config['aave']['abi_path'], 'r') as file:
    aave_abi = json.load(file)  # Load ABI directly if it's a list
with open(config['compound']['abi_path'], 'r') as file:
    compound_abi = json.load(file)  # Load ABI directly if it's a list

# Initialize contracts
aave_contract = web3.eth.contract(address=aave_address, abi=aave_abi)
compound_contract = web3.eth.contract(address=compound_address, abi=compound_abi)

wallet_address = config['web3']['wallet_address']
private_key = config['web3']['private_key']

# Function to interact with Aave
def check_aave_yield():
    try:
        # Example function call: Get some data from the Aave contract
        reserve_data = aave_contract.functions.getReserveData(wallet_address).call()
        print(f"Aave Reserve Data: {reserve_data}")
    except Exception as e:
        print(f"Error fetching Aave reserves: {e}")

# Function to interact with Compound
def check_compound_yield():
    try:
        # Example function call: Get some data from the Compound contract
        account_liquidity = compound_contract.functions.getAccountLiquidity(wallet_address).call()
        print(f"Compound Account Liquidity: {account_liquidity}")
    except Exception as e:
        print(f"Error fetching Compound data: {e}")

# Function to run the bot periodically
def run_yield_farming_bot():
    while True:
        print("Checking Aave and Compound for yield farming opportunities...")
        check_aave_yield()
        check_compound_yield()
        time.sleep(3600)

if __name__ == "__main__":
    run_yield_farming_bot()
