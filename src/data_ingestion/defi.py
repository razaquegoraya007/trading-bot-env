from web3 import Web3

# Initialize Web3 connection
web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/aa2aabae9e7b469e9bd818a1dcf53489'))

# Use the correct method to convert the address to a checksummed address
lending_pool_address = web3.to_checksum_address('0x398EC7346DcD622eDc5ae82352F02bE94C62d119')

# Use this checksummed address in the contract interaction
lending_pool = web3.eth.contract(address=lending_pool_address, abi=[])

# Example: Fetch some data (you'll need to fill in the ABI and methods)
print("Data fetched from Aave")
