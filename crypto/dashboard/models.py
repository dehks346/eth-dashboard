from django.db import models

# Create your models here.
class EthPrice(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    gbp_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.timestamp} - £{self.gbp_price}"

class WalletBalance(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    eth_balance = models.DecimalField(max_digits=20, decimal_places=8)
    eth_price = models.DecimalField(max_digits=20, decimal_places=8)
    wallet_value = models.DecimalField(max_digits=20, decimal_places=8)