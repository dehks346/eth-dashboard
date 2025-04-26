from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('latest-price/', views.get_latest_price, name='latest-price'),
    path('eth-trends/', views.eth_trends_view, name='eth-trends-view'),
    path('wallet-trends/', views.wallet_trends_view, name='wallet-trends'),
    path('wallet-value/<str:address>/', views.wallet_value_view, name='wallet-value'),  # Added <str:address>
    path('historical-data/', views.historical_data, name='historical data')
]