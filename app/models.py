from django.db import models


class Category(models.Model):
    """Model for type of transaction."""

    type = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.type


class Budget(models.Model):
    """Model for income - expenses records."""

    amount = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    transaction_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.category.type} {self.amount} of {self.transaction_at}'