from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.IntegerField()
    current_price = models.ForeignKey('Bid', on_delete=models.CASCADE, related_name="listings")
    image = models.URLField(blank=True)
    category = models.CharField(max_length=64, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    comments = models.ManyToManyField('Comment', blank=True, related_name="listings")
    active = models.BooleanField(default=True)
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")
    

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    bid = models.IntegerField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", null=True)


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    message = models.TextField()
