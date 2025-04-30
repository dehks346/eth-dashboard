from django.shortcuts import render, redirect
from django.http import JsonResponse
from .web3_utils import get_recent_transactions, get_trends
from .models import EthPrice, WalletBalance
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

def dashboard(request):
    wallet_address = '0x1bD580113B02F39e441d5D2A3A15cA56E8170E07'
    recent_txs = get_recent_transactions()
    try:
        latest = EthPrice.objects.latest('timestamp')
        eth_balance = WalletBalance.objects.latest('timestamp').eth_balance
        wallet_value = Decimal(str(eth_balance)) * latest.gbp_price
    except EthPrice.DoesNotExist:
        wallet_value = 0

    context = {
        'wallet_address': wallet_address,
        'eth_balance': eth_balance,
        'recent_txs': recent_txs,
        'wallet_value': wallet_value,
        'latest_eth_price': latest.gbp_price,
        'latest_eth_timestamp': latest.timestamp,
    }
    return render(request, 'dashboard/dashboard.html', context)

def get_latest_price(request):
    try:
        latest = EthPrice.objects.latest('timestamp')
        data = {
            'gbp_price': float(latest.gbp_price),
            'timestamp': latest.timestamp.isoformat()
        }
    except EthPrice.DoesNotExist:
        data = {'error': 'Price data not available'}
    return JsonResponse(data)

def eth_trends_view(request):
    data = get_trends()
    eth_trends = data.get('eth', {'1h': None, '24h': None, '7d': None, 'all': None})
    return JsonResponse(eth_trends)

def wallet_trends_view(request):
    data = get_trends()
    wallet_trends = data.get('wallet', {'1h': None, '24h': None, '7d': None, 'all': None})
    if all(v is None for v in wallet_trends.values()):
        return JsonResponse({'error': 'Wallet trends data not available'}, status=404)
    return JsonResponse(wallet_trends)

def wallet_value_view(request, address):
    try:
        data = WalletBalance.objects.latest('timestamp')
        new_data = {'eth': float(data.eth_balance)}
    except WalletBalance.DoesNotExist:
        new_data = {'error': 'Wallet balance data not available'}
    return JsonResponse(new_data)

def historical_data(request):
    timeframe = request.GET.get('timeframe', '1h')
    now = timezone.now()

    if timeframe == '1h':
        start_time = now - timedelta(hours=1)
    elif timeframe == '24h':
        start_time = now - timedelta(hours=24)
    elif timeframe == '7d':
        start_time = now - timedelta(days=7)
    else:
        start_time = now - timedelta(days=3650)

    eth_prices = EthPrice.objects.filter(timestamp__gte=start_time).order_by('timestamp')
    wallet_values = WalletBalance.objects.filter(timestamp__gte=start_time).order_by('timestamp')

    response_data = {
        'eth_prices': [
            {'timestamp': p.timestamp.isoformat(), 'gbp_price': str(p.gbp_price)}
            for p in eth_prices
        ],
        'wallet_values': [
            {'timestamp': w.timestamp.isoformat(), 'value': str(w.wallet_value)}
            for w in wallet_values
        ],
    }

    return JsonResponse(response_data)