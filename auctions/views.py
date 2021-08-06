from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import datetime
from .models import Listing, User, Bid, Watchlist, Comment
from . import util

categories_list = ["Books", "Sports", "Electronics", "Grocery", "Home", "Toys", "Clothing", "Other"]

def index(request):
    #print("--__---____-----_____")
    active_listings = Listing.objects.filter(active=True)
    #print("active listings:")
    #print(active_listings)
    price = {}
    i = 0
    for listing in active_listings:
        
        #print("No: "+ str(i) + " " + str(listing.item_name) + " costs €" + str(util.highest_bid(listing).price))
        #print("price["+str(listing.item_id)+"] = "+ str(util.highest_bid(listing).price))

        price.update({ listing.item_id : str(util.highest_bid(listing).price) })
        i += 1
        
    #print("pricing fn returns: ")
    #print(price)
    return render(request, "auctions/index.html", {
        "listings" : Listing.objects.filter(active=True),
        "users" : User.objects.all(),
        "prices" : price
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def new_listing(request):
    if request.method == "POST":

        seller = request.user.id
        item_name = request.POST["listing_name"]
        description = request.POST["content"]
        image = request.POST["image_url"]
        st_price = request.POST["price"]
        creation_date = datetime.datetime.now()
        category = request.POST["category"]
        #below print statements are for testing
        #print("seller id is: "+str(seller))
        #print("item name is: "+item_name)
        #print("content is: "+description)
        #print("image is: "+image)
        #print("start price is: "+st_price)
        #print("Time is: "+str(creation_date))
        #print("The category is: " + category)

        if not seller:
            return render(request, "auctions/register.html", {
                "message": "Please log in"
            })
        
        if not item_name:
            return render(request, "auction/new_listing.html", {
                "message" : "Please provide a name for listing"
            })

        if not description:
            return render(request, "auction/new_listing.html", {
                "message" : "Please provide a description for listing"
            })

        if not image:
            return render(request, "auction/new_listing.html", {
                "message" : "Please provide an image for listing"
            })

        if not st_price:
            return render(request, "auction/new_listing.html", {
                "message" : "Please provide a price for listing"
            })

        try:
            listing = Listing(creation_date = creation_date, image=image, item_name=item_name, description=description, seller=request.user, st_price=st_price, cur_price=st_price, active=True, category=category)
            listing.save()
            item = Listing.objects.get(creation_date=creation_date, seller=request.user, item_name=item_name)
            #print(item)
            bid = Bid(item=item, price=st_price, bidder=request.user)
            bid.save()
        except IntegrityError:
            return render(request, "auctions/new_listing.html", {
                "message": "name already taken."
            })

        #print(Listing)
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/new_listing.html", {
        "categories" : categories_list
    })


def listing(request, item_id):
    
    if request.method == "POST":
        
        # This checks that the logged in user is the seller
        if request.user == Listing.objects.get(item_id=item_id).seller:
            # This allows the seller to close the auction
            if request.POST["status"] == "close":
                cur_listing = Listing.objects.get(item_id=item_id)
                cur_listing.active = False
                cur_listing.save()
                return render(request, "auctions/listing.html", {
                    "message" : "The listing is now closed. \rThe winner is "+ str(util.highest_bid(item_id).bidder),
                    "listing" : Listing.objects.get(item_id = item_id),
                    "current_price" : util.highest_bid(item_id),
                    "watch_btn" : util.watch_btn(request.user, Listing.objects.get(item_id = item_id)),
                    "comments" : Comment.objects.filter(item_id = item_id)
                })
        else:
            
            

            #take in the bid.
            new_bid = float(request.POST["bid"])
            if not new_bid:
                return render(request, "auctions/listing.html", {
                    "message" : "Please provide an value for your bid",
                    "listing" : Listing.objects.get(item_id = item_id),
                    "current_price" : util.highest_bid(item_id),
                    "watch_btn" : util.watch_btn(request.user, Listing.objects.get(item_id = item_id)),
                    "comments" : Comment.objects.filter(item_id = item_id)                   
                })

            if new_bid <= int(util.highest_bid(item_id).price):
                return render(request, "auctions/listing.html", {
                    "message" : "You must bid higher than current bid",
                    "listing" : Listing.objects.get(item_id = item_id),
                    "current_price" : util.highest_bid(item_id),
                    "watch_btn" : util.watch_btn(request.user, Listing.objects.get(item_id = item_id)),
                    "comments" : Comment.objects.filter(item_id = item_id)
                })
                
            
            listing = Listing(item_id=item_id)
            # set as new highest bid
            new_highest_bid=Bid(item=listing, price=new_bid, bidder=request.user)
            new_highest_bid.save()
            # to update price
            listing0 = Listing.objects.get(item_id = item_id)
            listing0.cur_price = new_bid
            listing0.save()
            
            return render(request, "auctions/listing.html", {
                    "message" : "You are now the highest bidder",
                    "listing" : Listing.objects.get(item_id = item_id),
                    "current_price" : util.highest_bid(item_id),
                    "watch_btn" : util.watch_btn(request.user, Listing.objects.get(item_id = item_id)),
                    "comments" : Comment.objects.filter(item_id = item_id)
                })
    
    
    listing = Listing.objects.get(item_id = item_id)
    current_price = util.highest_bid(item_id)
    
    return render(request, "auctions/listing.html",{
        "listing" : listing,
        "current_price" : current_price,
        "watch_btn" : util.watch_btn(request.user, listing),
        "comments" : Comment.objects.filter(item_id = item_id)
    })

def watchlist(request):
    watchlist = Watchlist.objects.filter(watcher_id = request.user)
    listings = Listing.objects.all()

    q = Listing.objects.filter(item_id = -1) # creates an empty queryset to add on
       
    for watchitem in watchlist:
        listitem = Listing.objects.filter(item_id = watchitem.item_id)
        q = listitem.union(listitem,q)
        
    listings = q
    
    return render(request, "auctions/watchlist.html", {
        "listings" : listings
    })
    
def comment(request):
    if request.method == "POST":
        listing = Listing(item_id=request.POST["item_id"])
        content = request.POST["content"]
        commenter = request.user
        date = datetime.datetime.now()
        comment = Comment(item = listing, content = content, commenter = commenter, date = date)
        comment.save()

        
        return render(request, "auctions/listing.html", {
                    "message" : "Comment added",
                    "listing" : Listing.objects.get(item_id = listing.item_id),
                    "current_price" : util.highest_bid(listing.item_id),
                    "watch_btn" : util.watch_btn(request.user, listing),
                    "comments" : Comment.objects.filter(item_id = listing.item_id)
                })
    
#this adds item to the users watchlist
def watch_toggle(request):
    if request.method == "POST":
        item_id = request.POST["item_id"]
        #if item is already on watchlist
        if Watchlist.objects.filter(item = item_id, watcher = request.user):
            #remove from watchlist
            Watchlist.objects.get(item = item_id, watcher = request.user).delete()
            return render(request, "auctions/listing.html", {
                "message" : "Removed from watchlist",
                "listing" : Listing.objects.get(item_id = item_id),
                "current_price" : util.highest_bid(item_id),
                "watch_btn" : util.watch_btn(request.user, Listing.objects.get(item_id = item_id)),
                "comments" : Comment.objects.filter(item_id = item_id) 
            })
        #add to watchlist
        listing = Listing(item_id=item_id)
        watchitem = Watchlist(item = listing, watcher = request.user)
        watchitem.save()
        return render(request, "auctions/listing.html", {
            "message" : "Added to watchlist",
            "listing" : Listing.objects.get(item_id = item_id),
            "current_price" : util.highest_bid(item_id),
            "watch_btn" : util.watch_btn(request.user, Listing.objects.get(item_id = item_id)),
            "comments" : Comment.objects.filter(item_id = item_id)
        })

def categories(request):
    if request.method == "POST":
        listings = Listing.objects.filter(category = request.POST["category"])
        return render(request, "auctions/categories.html", {
            "categories" : categories_list,
            "category" : request.POST["category"],
            "listings" : listings
        })  
    return render(request, "auctions/categories.html", {
        "categories" : categories_list
    })    