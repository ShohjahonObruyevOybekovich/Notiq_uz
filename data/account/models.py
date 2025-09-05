from django.db import models
from django.utils.crypto import get_random_string


class Customer(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, null=True)
    dlr_webhook = models.URLField(blank=True, null=True)
    mo_webhook = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class ApiKey(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="api_keys")
    key = models.CharField(max_length=64, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = get_random_string(48)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.name} :: {self.key[:6]}…"
