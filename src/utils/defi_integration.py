from web3 import Web3
import json
import os
import yaml

# Load configuration from config.yaml
config_path = os.path.join(os.path.dirname(__file__), '../../config/config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# Connect to Ethereum using Infura
infura_url = config['web3']['infura_url']
web3 = Web3(Web3.HTTPProvider(infura_url))

# Check if connected to the Ethereum network
if not web3.is_connected():  # Updated method name
    print("Failed to connect to the Ethereum network. Check your Infura URL.")
else:
    print("Successfully connected to the Ethereum network.")

# Convert contract addresses to checksummed addresses
aave_address = Web3.to_checksum_address(config['aave']['contract_address'])  # Corrected method name
compound_address = Web3.to_checksum_address(config['compound']['contract_address'])  # Corrected method name

# Load ABIs
with open(config['aave']['abi_path'], 'r') as abi_file:
    aave_abi = json.load(abi_file)

with open(config['compound']['abi_path'], 'r') as abi_file:
    compound_abi = json.load(abi_file)

# Create contract instances
try:
    aave_contract = web3.eth.contract(address=aave_address, abi=aave_abi)
    print(f"Connected to Aave contract at {aave_address}")
except Exception as e:
    print(f"Error connecting to Aave contract: {e}")

try:
    compound_contract = web3.eth.contract(address=compound_address, abi=compound_abi)
    print(f"Connected to Compound contract at {compound_address}")
except Exception as e:
    print(f"Error connecting to Compound contract: {e}")

# Function to invest in Aave
def invest_in_aave(amount):
    try:
        print(f"Investing {amount} in Aave...")
        # Add your investment logic here
    except Exception as e:
        print(f"Error investing in Aave: {e}")

# Function to invest in Compound
def invest_in_compound(amount):
    try:
        print(f"Investing {amount} in Compound...")
        # Add your investment logic here
    except Exception as e:
        print(f"Error investing in Compound: {e}")

# Function to check yield rates and make reinvestment decisions
def check_yield_and_reinvest():
    try:
        # Compare yield rates between Aave and Compound
        # For now, we simulate this decision-making process
        aave_yield = 0.03  # Example yield rate
        compound_yield = 0.04  # Example yield rate

        if compound_yield > aave_yield:
            invest_in_compound(100)  # Example amount
        else:
            invest_in_aave(100)  # Example amount
    except Exception as e:
        print(f"Error checking yield rates: {e}")
