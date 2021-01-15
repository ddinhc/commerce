from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, related_name="watchlist")

class Catagory(models.Model):
    tag = models.CharField(max_length=23)

    def __str__(self):
        return f"{self.tag} "

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image = models.ImageField(blank=True, null=True, upload_to="images/")
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    catagory = models.ManyToManyField(Catagory, blank=True, related_name="catagory")

    def __str__(self):
        return f"Listing {self.id}: {self.title}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid {self.id}: Listing {self.listing.id} "


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s comments "
