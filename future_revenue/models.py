from django.conf import settings
from django.db import models



class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(ProductCategory, related_name="products", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class SalesData(models.Model):
    product = models.ForeignKey(Product, related_name="sales", on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    sales_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.date}"
