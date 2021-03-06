from django.db import models
from profiles.models import UserProfile
from products.models import Product


class Reviews(models.Model):
    """
    Reviews model for CRUD operations
    """
    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    # Rating values
    RATE = [(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    rating = models.IntegerField(choices=RATE)
    date_posted = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
