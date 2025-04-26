from web3 import Web3
from decouple import config
import requests
from django.http import JsonResponse
from django.utils import timezone
from .models import EthPrice, WalletBalance
from datetime import timedelta
from decimal import Decimal  # Added import for Decimal
import logging
from datetime import datetime


INFURA_URL = config('INFURA_URL')
ETHERSCAN_API_KEY = config('ETHERSCAN_API_KEY')

web3 = Web3(Web3.HTTPProvider(INFURA_URL))

if not web3.is_connected():
    raise Exception('Failed to connect to Ethereum network: ' + str(INFURA_URL))

def get_recent_transactions(count=10):
    address = '0x1bD580113B02F39e441d5D2A3A15cA56E8170e07'
    url = (
        f"https://api.etherscan.io/api"
        f"?module=account"
        f"&action=txlist"
        f"&address={address}"
        f"&startblock=0"
        f"&endblock=99999999"
        f"&sort=desc"
        f"&apikey={ETHERSCAN_API_KEY}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data['status'] != '1':
            return []

        transactions = data['result'][:count]
        cleaned_transactions = []

        for tx in transactions:
            value_wei = int(tx['value'])
            value_eth = Web3.from_wei(value_wei, 'ether')
            timestamp = datetime.fromtimestamp(int(tx['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S')
            status = 'Success' if tx['isError'] == '0' else 'Failed'

            cleaned_tx = {
                'hash': tx['hash'],
                'timestamp': timestamp,
                'from': tx['from'],
                'to': tx['to'],
                'value_eth': float(value_eth),
                'gas_used': int(tx['gasUsed']),
                'status': status
            }
            cleaned_transactions.append(cleaned_tx)

        return cleaned_transactions

    except requests.RequestException:
        return []
    except Exception:
        return []

def get_eth_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {'ids': 'ethereum', 'vs_currencies': 'gbp'}
    response = requests.get(url, params=params).json()
    try:
        return response["ethereum"]["gbp"]
    except KeyError:
        print("Error: 'ethereum' key not found in response")
        return None

def calculate_change(reference_time, model, field, balance=None):
    """
    Calculate percentage and price change for ETH price or wallet value.
    - model: EthPrice or WalletBalance
    - field: 'gbp_price' for EthPrice, 'eth_balance' for WalletBalance
    - balance: ETH balance for wallet calculations (optional)
    """
    try:
        latest = EthPrice.objects.latest('timestamp')
        old = model.objects.filter(timestamp__lte=reference_time).order_by('timestamp').first()
        if not old or getattr(old, field) is None:
            return None

        if model == EthPrice:
            old_value = getattr(old, field)
            new_value = latest.gbp_price
        else:  # WalletBalance
            if not balance:
                balance = getattr(old, field)
            # Convert balance to Decimal to match gbp_price type
            balance = Decimal(str(balance))
            old_price = EthPrice.objects.filter(timestamp__lte=reference_time).order_by('timestamp').first().gbp_price
            old_value = balance * old_price
            new_value = balance * latest.gbp_price

        percent_diff = ((new_value - old_value) / old_value) * 100
        price_diff = new_value - old_value
        return {'percent': float(percent_diff), 'price': float(price_diff)}  # Convert to float for JSON serialization
    except (EthPrice.DoesNotExist, WalletBalance.DoesNotExist):
        return None


logger = logging.getLogger(__name__)

def get_trends():
    now = timezone.now()
    timeframes = {
        '1h': now - timedelta(hours=1),
        '24h': now - timedelta(hours=24),
        '7d': now - timedelta(days=7),
        'all': None
    }
    
    eth_trends = {}
    wallet_trends = {}
    
    for timeframe, start_time in timeframes.items():
        # ETH Price Trends
        if start_time:
            prices = EthPrice.objects.filter(timestamp__gte=start_time).order_by('timestamp')
        else:
            prices = EthPrice.objects.all().order_by('timestamp')
        
        logger.debug(f"Timeframe {timeframe}: {prices.count()} EthPrice entries")
        if prices.count() >= 2:
            first_price = prices.first().gbp_price
            last_price = prices.last().gbp_price
            percent = ((last_price - first_price) / first_price * 100) if first_price else 0
            price_diff = last_price - first_price
            eth_trends[timeframe] = {'percent': float(percent), 'price': float(price_diff)}
            logger.debug(f"ETH {timeframe}: percent={percent:.2f}, price_diff={price_diff}")
        else:
            eth_trends[timeframe] = {'percent': None, 'price': None}
            logger.debug(f"ETH {timeframe}: insufficient data")
        
        # Wallet Value Trends
        if start_time:
            balances = WalletBalance.objects.filter(timestamp__gte=start_time).order_by('timestamp')
        else:
            balances = WalletBalance.objects.all().order_by('timestamp')
        
        logger.debug(f"Timeframe {timeframe}: {balances.count()} WalletBalance entries")
        if balances.count() >= 2:
            first_balance = balances.first().eth_balance
            last_balance = balances.last().eth_balance
            first_price = EthPrice.objects.filter(timestamp__lte=balances.first().timestamp).order_by('-timestamp').first()
            last_price = EthPrice.objects.filter(timestamp__lte=balances.last().timestamp).order_by('-timestamp').first()
            if first_price and last_price:
                first_value = Decimal(str(first_balance)) * first_price.gbp_price
                last_value = Decimal(str(last_balance)) * last_price.gbp_price
                percent = float((last_value - first_value) / first_value * 100) if first_value else 0
                value_diff = float(last_value - first_value)
                wallet_trends[timeframe] = {'percent': percent, 'price': value_diff}
                logger.debug(f"Wallet {timeframe}: percent={percent:.2f}, value_diff={value_diff}")
            else:
                wallet_trends[timeframe] = {'percent': None, 'price': None}
                logger.debug(f"Wallet {timeframe}: missing price data")
        else:
            wallet_trends[timeframe] = {'percent': None, 'price': None}
            logger.debug(f"Wallet {timeframe}: insufficient balance data")
    
    return {'eth': eth_trends, 'wallet': wallet_trends}