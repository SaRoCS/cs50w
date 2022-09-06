from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    watch_item = models.ManyToManyField('Listing', blank=True, related_name="watchers")
    def __str__(self):
        return f"{self.username}"

class Listing(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=7)
    title = models.CharField(max_length=127)
    description = models.CharField(max_length=2048)
    image = models.CharField(blank=True, max_length=256)
    category = models.CharField(blank=True, max_length=32)
    lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listing')
    is_active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    value = models.DecimalField(decimal_places=2, max_digits=7)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bidder')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')

    def __str__(self):
        return f"{self.value}"

class Comment(models.Model):
    comment = models.CharField(max_length=2048)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commenter')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comment')

    def __str__(self):
        return f"{self.comment}"


