from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    
    def __str__(self):
        return f"{self.username}"

class Listing(models.Model):
    item_id = models.IntegerField(primary_key=True)
    creation_date = models.DateTimeField()
    image = models.CharField(max_length=64)
    item_name = models.CharField(max_length=64)
    description = models.TextField()
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items_for_sale")
    st_price = models.FloatField()
    cur_price = models.FloatField()
    active = models.BooleanField()
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.item_id} {self.item_name}"


class Bid(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    price = models.FloatField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name= "items_bid_on")
    def __str__(self):
        return f"{self.price} from {self.bidder}"

class Comment(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.commenter} {self.date}"
    
class Watchlist(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchers")
    watcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watching")

    def __str__(self):
        return f"{self.item} watched by {self.watcher}"
   
