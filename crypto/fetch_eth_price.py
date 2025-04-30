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


logging.basicConfig(filename='eth_price_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')



def fetch_and_store_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {'ids': 'ethereum', 'vs_currencies': 'gbp'}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        try:
            gbp_price = Decimal(str(data['ethereum']['gbp'])).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            latest_price_obj = EthPrice.objects.latest('timestamp')
            latest_price = latest_price_obj.gbp_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            if gbp_price != latest_price:
                EthPrice.objects.create(gbp_price=gbp_price)
                logging.info(f"Price stored: {gbp_price}")
            else:
                logging.info(f"no change in price: {gbp_price}, value not stored")

        except (KeyError, EthPrice.DoesNotExist):
            # Save if there's no existing record yet
            EthPrice.objects.create(gbp_price=gbp_price)
            logging.info(f"Initial price stored: {gbp_price}")
    else:
        logging.error(f"Error fetching price: {response.status_code}")


def fetch_and_store_wallet_balance(address):
    try:
        # Fetch balance in wei and convert to ETH
        balance_wei = web3.eth.get_balance(address)
        eth_balance = web3.from_wei(balance_wei, 'ether')

        # Convert to Decimal with safe rounding
        eth_balance = Decimal(str(eth_balance)).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)

        # Fetch latest ETH price in GBP
        latest_price = EthPrice.objects.latest('timestamp').gbp_price
        latest_price = Decimal(str(latest_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Calculate wallet value
        wallet_value = (eth_balance * latest_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # Check for duplicates before storing
        try:
            latest_snapshot = WalletBalance.objects.latest('timestamp')
            previous_value = latest_snapshot.wallet_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            if wallet_value != previous_value:
                WalletBalance.objects.create(
                    eth_balance=eth_balance,
                    eth_price=latest_price,
                    wallet_value=wallet_value,
                    timestamp=timezone.now()
                )
                logging.info(f"New balance stored for {address}: {eth_balance} ETH")
            else:
                logging.info(f"No change in balance for {address}, skipping store.")
        except WalletBalance.DoesNotExist:
            WalletBalance.objects.create(
                eth_balance=eth_balance,
                eth_price=latest_price,
                wallet_value=wallet_value,
                timestamp=timezone.now()
            )
            logging.info(f"Initial balance stored for {address}: {eth_balance} ETH")

    except Exception as e:
        logging.error(f"Error storing wallet balance for {address}: {str(e)}")

def periodic_task():
    wallet_address = "0x1bD580113B02F39e441d5D2A3A15cA56E8170E07"

    fetch_and_store_price()  # Store the Ethereum price
    fetch_and_store_wallet_balance(wallet_address)  # Store the wallet balance

periodic_task()
