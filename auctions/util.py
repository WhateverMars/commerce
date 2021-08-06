from django.contrib.auth.models import AnonymousUser
from .models import Bid, Listing, Watchlist

def highest_bid(listing_id):
    # This function reads through the bids table in db and checks the highest value for a listing.
    item_bids = Bid.objects.filter(item=listing_id)
    highest_bid = item_bids.order_by("-price")[0]
    return highest_bid

def watch_btn(user,item):
    if str(user) is str(AnonymousUser()):
        
        return("Sign in to add to Watchlist")
    if Watchlist.objects.filter(item = item, watcher = user):
        return("Remove from Watchlist")
    else:
        return("Add to Watchlist")