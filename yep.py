import random
import string
import requests
from eth_account import Account
import time

# Your Etherscan API keys (replace these with your real API keys)
ETHERSCAN_API_KEYS = [
    '5K221ME7PYP5RUE1E1CBCB8WU2UV3EMKDS',  # Your API key 1
    'QQVKPQFWG7X2NU67549KEEH2RMVJS3KCPW',  # Your API key 2
    'JPPXZJ51MRYMKWBXMPCU266M6DNK8J5MXR'   # Your API key 3
]
ETHERSCAN_API_URL = "https://api.etherscan.io/api"

# Function to generate random private key
def generate_random_private_key():
    return ''.join(random.choices(string.hexdigits.lower(), k=64))

# Function to check if an address has at least 14 unique characters
def has_unique_characters(address, required_unique_chars=14):
    unique_chars = set(address)
    return len(unique_chars) >= required_unique_chars

# Function to generate address from private key
def generate_address_from_private_key(private_key):
    account = Account.from_key(private_key)  # Correct method to generate address
    return account.address

# Function to check balance using Etherscan API
def check_balance(address, api_key):
    params = {
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest",
        "apikey": api_key
    }

    response = requests.get(ETHERSCAN_API_URL, params=params)
    data = response.json()

    if data['status'] == '1':
        balance = int(data['result']) / 10**18  # Convert Wei to Ether
        return balance
    else:
        return None

# Function to log addresses with balance greater than 0.005 ETH to logs.txt
def log_to_file(address, private_key, balance):
    with open("logs.txt", "a") as log_file:
        log_file.write(f"Address: {address}\n")
        log_file.write(f"Private Key: {private_key}\n")
        log_file.write(f"Balance: {balance} ETH\n")
        log_file.write("\n")  # Add a new line for separation

# Function to check balances for random generated private keys
def check_random_keys():
    count = 0
    while True:
        private_key = generate_random_private_key()
        address = generate_address_from_private_key(private_key)

        # Skip if the address doesn't have at least 14 unique characters
        if not has_unique_characters(address):
            continue

        # Rotate API keys to avoid rate limiting
        api_key = ETHERSCAN_API_KEYS[count % len(ETHERSCAN_API_KEYS)]

        balance = check_balance(address, api_key)

        if balance is not None:
            if balance > 0.005:
                print(f"Found address with balance over 0.005 ETH!")
                print(f"Address: {address}")
                print(f"Private Key: {private_key}")
                print(f"Balance: {balance} ETH")

                # Log to a file
                log_to_file(address, private_key, balance)

            else:
                print(f"Checked address {address}, balance is below 0.005 ETH.")
        else:
            print(f"Error fetching balance for address {address}.")

        count += 1
        time.sleep(1)  # To avoid rate limiting issues with Etherscan API

# Main function to run the script
def main():
    print("Starting random key generation and balance checking...")
    check_random_keys()

if __name__ == "__main__":
    main()
