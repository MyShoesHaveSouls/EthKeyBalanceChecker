import asyncio
import httpx
import logging
from Crypto.Hash import keccak
import ecdsa
import binascii
import itertools
import secrets  # For cryptographically secure random key generation
from tqdm import tqdm  # Progress bar

logging.basicConfig(level=logging.INFO)

# Function to write balances to file
def save_to_file(data):
    with open("balances.txt", "a") as f:
        f.write(data + "\n")

# Function to distribute API keys evenly across threads
def distribute_api_keys(keys, num_threads):
    key_iterator = itertools.cycle(keys)
    return [next(key_iterator) for _ in range(num_threads)]

# Function to get user input with validation
def get_user_input(prompt, condition):
    while True:
        try:
            value = int(input(prompt))
            if not condition(value):
                print(f"Invalid input: {prompt}")
                continue
            return value
        except ValueError:
            print("Error: value should be in integer format")

# Collecting user inputs
start_value = get_user_input("Start value: ", lambda x: x > 0)
end_value = get_user_input("End value: ", lambda x: x > start_value)

# Set default values for threads and batch size
number_of_threads = 4  # Set the number of threads
no_of_accounts = 100  # Set the number of accounts per batch

check_in_thread = (end_value - start_value) // number_of_threads

# List of API keys
api_keys = [
    'F92Z14GE2DTF6PBBYY1YPHPJ438PT3P2VI',
    '4Q5U7HNF4CGTVTGEMGRV5ZU9WYNJ6N7YA5',
    'EX8K12JY7BCVG8RAUU8X2Z6QT2GCF5EYB4',
    'DZHWCIEA2WW86CZEC88IGWG1JFB6JN3VHS'
]

# Function to check if the address has at least 16 unique characters
def has_unique_characters(address):
    # Remove the '0x' prefix
    address = address[2:]
    unique_chars = set(address)
    return len(unique_chars) >= 16

# Function to generate Ethereum address from a random private key
async def generate_address(private_key, num):
    addresses = []
    for i in range(num):
        private_key_hex = private_key.hex()
        sk = ecdsa.SigningKey.from_string(binascii.unhexlify(private_key_hex), curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        public_key = vk.to_string()
        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(public_key)
        public_key_hash = keccak_hash.digest()
        ethereum_address = "0x" + public_key_hash.hex()[-40:]
        
        # Only add addresses with 16 unique characters
        if has_unique_characters(ethereum_address):
            addresses.append(ethereum_address)
    return addresses

# Function to get balance of Ethereum addresses
async def get_balance(addresses, api_key, client):
    url = f'https://api.etherscan.io/api?module=account&action=balancemulti&address={"".join(addresses)}&tag=latest&apikey={api_key}'
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Error fetching balance: {e}")
    return None

# Function to process the balance response
async def process_balance_response(response, start, no_of_accounts):
    if response and 'status' in response and response['status'] == '1':
        for index, rec in enumerate(response['result']):
            hex_id = start + index
            balance_wei = int(rec['balance'])
            if balance_wei > 0:
                entry = f"{hex_id} {rec['account']} {balance_wei / 1e18} ETH"
                logging.info(entry)
                save_to_file(entry)
    else:
        logging.error(f"Invalid response: {response}")

# Function to run the balance check process
async def run_batch(batch_index, start, no_of_accounts, api_key, client, pbar):
    # Generate a random 32-byte private key for each batch
    private_key = secrets.token_bytes(32)  # Random 256-bit private key
    
    addresses = await generate_address(private_key, no_of_accounts)
    response = await get_balance(addresses, api_key, client)
    await process_balance_response(response, start, no_of_accounts)
    pbar.update(1)  # Update the progress bar after processing a batch

# Function to run multiple threads
async def run_multiple_threads():
    tasks = []
    global start_value
    distributed_api_keys = distribute_api_keys(api_keys, number_of_threads)
    
    # Initialize the progress bar for the total number of batches
    total_batches = (end_value - start_value) // no_of_accounts
    pbar = tqdm(total=total_batches, desc="Processing Batches", unit="batch")
    
    async with httpx.AsyncClient() as client:
        for thread_index in range(number_of_threads):
            tasks.append(run_batch(thread_index, start_value, no_of_accounts, distributed_api_keys[thread_index], client, pbar))
            start_value += check_in_thread
        
        # Wait for all tasks to finish
        await asyncio.gather(*tasks)

    pbar.close()  # Close the progress bar when done

if __name__ == "__main__":
    asyncio.run(run_multiple_threads())
