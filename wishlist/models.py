from django.db import models
from django.contrib.auth.models import User
from products.models import Product

from django.db.models.signals import post_save
from django.dispatch import receiver


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return self.user.username


# Creates a wishlist for new users
@receiver(post_save, sender=User)
def create_or_update_the_Wishlist(sender, instance, created, **kwargs):
    ''' creates the user profile or updates it if there is one already '''
    if created:
        Wishlist.objects.create(user=instance)
    instance.userprofile.save()
