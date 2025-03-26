import asyncio
import httpx
import logging
from Crypto.Hash import keccak
import ecdsa
import binascii
import itertools

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
number_of_threads = get_user_input("Number of threads: ", lambda x: x > 0)
no_of_accounts = get_user_input("Number of accounts per batch: ", lambda x: x > 0)
check_in_thread = (end_value - start_value) // number_of_threads

# List of API keys
api_keys = [import asyncio
import httpx
import logging
from Crypto.Hash import keccak
import ecdsa
import binascii
import itertools

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
number_of_threads = get_user_input("Number of threads: ", lambda x: x > 0)
no_of_accounts = get_user_input("Number of accounts per batch: ", lambda x: x > 0)
check_in_thread = (end_value - start_value) // number_of_threads

# List of API keys
api_keys = [
    '5K221ME7PYP5RUE1E1CBCB8WU2UV3EMKDS',
    'QQVKPQFWG7X2NU67549KEEH2RMVJS3KCPW',
    'JPPXZJ51MRYMKWBXMPCU266M6DNK8J5MXR'
]

# Function to generate Ethereum address from private key
async def generate_address(private_key, num):
    addresses = []
    for i in range(num):
        private_key_hex = hex(private_key + i)[2:].zfill(64)
        sk = ecdsa.SigningKey.from_string(binascii.unhexlify(private_key_hex), curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        public_key = vk.to_string()
        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(public_key)
        public_key_hash = keccak_hash.digest()
        ethereum_address = "0x" + public_key_hash.hex()[-40:]
        
        # Only add address if it contains at least 16 unique characters/numbers
        if len(set(ethereum_address[2:])) >= 16:
            addresses.append(ethereum_address)
        else:
            logging.info(f"Skipping address {ethereum_address} due to insufficient unique characters.")
    
    # Log generated addresses
    logging.info(f"Generated addresses: {addresses}")
    return addresses

# Function to get balance of Ethereum addresses
async def get_balance(addresses, api_key, client):
    if not addresses:
        logging.warning("No addresses to check.")
        return None
    
    url = f'https://api.etherscan.io/api?module=account&action=balancemulti&address={"".join(addresses)}&tag=latest&apikey={api_key}'
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error occurred: {e}")
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
async def run_batch(batch_index, start, no_of_accounts, api_key, client):
    addresses = await generate_address(start, no_of_accounts)
    response = await get_balance(addresses, api_key, client)
    await process_balance_response(response, start, no_of_accounts)

# Function to run multiple threads
async def run_multiple_threads():
    tasks = []
    global start_value
    distributed_api_keys = distribute_api_keys(api_keys, number_of_threads)
    async with httpx.AsyncClient() as client:
        for thread_index in range(number_of_threads):
            tasks.append(run_batch(thread_index, start_value, no_of_accounts, distributed_api_keys[thread_index], client))
            start_value += check_in_thread
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(run_multiple_threads())
