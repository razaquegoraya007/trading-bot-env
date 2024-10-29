from web3 import Web3

web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/aa2aabae9e7b469e9bd818a1dcf53489'))

lending_pool_address = web3.to_checksum_address('0x398EC7346DcD622eDc5ae82352F02bE94C62d119')

lending_pool = web3.eth.contract(address=lending_pool_address, abi=[])

print("Data fetched from Aave")
