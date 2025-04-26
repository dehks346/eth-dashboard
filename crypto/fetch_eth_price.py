import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crypto.settings")

import django
django.setup()

import requests
import logging
from dashboard.models import EthPrice, WalletBalance
import time
from web3 import Web3
from decouple import config
from django.utils import timezone
import datetime
from decimal import Decimal, ROUND_HALF_UP

# Your Web3 provider URL
INFURA_URL = config('INFURA_URL')
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

if not web3.is_connected():
    raise Exception('Failed to connect to the Ethereum network.')

def get_eth_balance(address):
    # Fetch balance in wei and convert to ETH
    balance_wei = web3.eth.get_balance(address)
    eth_balance = web3.from_wei(balance_wei, 'ether')
    
    # Fetch latest ETH price in GBP
    latest_price = EthPrice.objects.latest('timestamp').gbp_price
    
    # Convert to Decimal for precision
    eth_balance = Decimal(str(eth_balance))  # Avoid float precision issues
    latest_price = Decimal(str(latest_price))
    
    # Calculate wallet value
    wallet_value = (eth_balance * latest_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    try:
        # Fetch the latest WalletBalance entry
        latest_entry = WalletBalance.objects.latest('timestamp')
        last_value = Decimal(str(latest_entry.wallet_value))  # Keep as Decimal
        last_price = Decimal(str(latest_entry.eth_price))    # Keep as Decimal
        last_time = latest_entry.timestamp

        # Calculate differences (all in Decimal)
        price_diff = abs(latest_price - last_price)
        value_diff = abs(wallet_value - last_value)
        time_diff = timezone.now() - last_time

        # Create new entry if conditions are met
        if price_diff > Decimal('0.01') or value_diff > Decimal('0.01') or time_diff.total_seconds() > 300:
            WalletBalance.objects.create(
                eth_balance=eth_balance,
                eth_price=latest_price,
                wallet_value=wallet_value,
                timestamp=timezone.now()
            )

    except WalletBalance.DoesNotExist:
        # Create first entry if no records exist
        WalletBalance.objects.create(
            eth_balance=eth_balance,
            eth_price=latest_price,
            wallet_value=wallet_value,
            timestamp=timezone.now()
        )

    return eth_balance


# Setup logging
logging.basicConfig(filename='eth_price_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def fetch_and_store_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {'ids': 'ethereum', 'vs_currencies': 'gbp'}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        try:
            gbp_price = data['ethereum']['gbp']
            EthPrice.objects.create(gbp_price=gbp_price)
            logging.info(f"Price stored: {gbp_price}")
        except KeyError:
            logging.error("Error extracting price from response.")
    else:
        logging.error(f"Error fetching price: {response.status_code}")

def fetch_and_store_wallet_balance(address):
    balance = get_eth_balance(address)
    logging.info(f"Balance stored for {address}: {balance} ETH")

def periodic_task():
    print('script is starting')
    # Specify your wallet address here
    wallet_address = "0x1bD580113B02F39e441d5D2A3A15cA56E8170E07"

    while True:
        fetch_and_store_price()  # Store the Ethereum price
        fetch_and_store_wallet_balance(wallet_address)  # Store the wallet balance
        print('ran successfully')
        time.sleep(15)  # Sleep for 60 seconds (1 minute)

# Start the periodic task
periodic_task()
