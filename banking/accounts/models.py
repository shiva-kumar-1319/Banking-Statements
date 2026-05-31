from django.db import models

class Account(models.Model):

    name=models.CharField(max_length=100)

    account_number=models.CharField(
        max_length=20,
        unique=True
    )

    balance=models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at=models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name