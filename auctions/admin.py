from django.contrib import admin

# Register your models here.
from .models import Listing, Bid, Comment

class ListingAdmin(admin.ModelAdmin):
    list_display = ("item_id", "item_name", "seller", "creation_date", "active", "cur_price")

class BidAdmin(admin.ModelAdmin):
    list_display = ("item", "bidder", "price")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("content", "commenter")


admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)