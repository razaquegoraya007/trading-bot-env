import requests

# Set the lower thresholds for testing
MIN_TVL = 1000
MIN_APY = 2
MemoryError

def fetch_defi_data():
    url = "https://api.llama.fi/protocols"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        filtered_protocols = []

        # Display all protocols and their details before filtering
        print("Checking All Protocols:")
        for protocol in data:
            # Extract values with defaults
            name = protocol.get('name', 'Unknown')
            tvl = protocol.get('tvl') if protocol.get('tvl') is not None else 0
            apy = protocol.get('apy') if protocol.get('apy') is not None else 0
            chain = protocol.get('chain', 'Unknown')

            # Print protocol info
            print(f"Protocol: {name}")
            print(f"  TVL: {tvl}")
            print(f"  APY: {apy}")
            print(f"  Chain: {chain}")
            print("-----")

            # Filter protocols meeting the threshold requirements
            if tvl >= MIN_TVL and apy >= MIN_APY:
                filtered_protocols.append({
                    "name": name,
                    "tvl": tvl,
                    "apy": apy,
                    "chain": chain
                })

        # Sort protocols by APY in descending order
        sorted_protocols = sorted(filtered_protocols, key=lambda x: x['apy'], reverse=True)

        # Display high-yield farming opportunities after filtering
        print("\nHigh-Yield Farming Opportunities (Sorted by APY):")
        for protocol in sorted_protocols:
            print(f"Protocol: {protocol['name']}")
            print(f"  TVL: ${protocol['tvl']:.2f}")
            print(f"  APY: {protocol['apy']}%")
            print(f"  Chain: {protocol['chain']}")
            print("-----")

        return sorted_protocols

    except requests.exceptions.RequestException as e:
        print(f"Error fetching DeFi data: {e}")
        return None

if __name__ == "__main__":
    fetch_defi_data()

