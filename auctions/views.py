from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, AuctionListing, Bid, Comment
from .forms import ListingForm, BiddingForm, CommentForm


def index(request):
    auction_listings = AuctionListing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "auction_listings": auction_listings
    })


def categories(request):
    avail_categories = AuctionListing.objects.values_list('category', flat=True).distinct().order_by().exclude(category='').filter(active=True)
    return render(request, "auctions/categories.html", {
        "categories": avail_categories
    })


def category_listing(request, category):
    avail_listings = AuctionListing.objects.filter(category=category, active=True)
    return render(request, "auctions/category_listing.html", {
        "category": category,
        "avail_listings": avail_listings
    })


@login_required(login_url='auctions/login.html')
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            title = request.POST['title']
            description = request.POST['description']
            starting_bid = request.POST['starting_bid']
            image = request.POST['image']
            category = request.POST['category']
            seller = request.user

            NULL_BID = Bid(bid=0)
            NULL_BID.save()
            current_price = NULL_BID

            new_listing = AuctionListing(title=title, description=description, starting_bid=starting_bid, image=image, category=category, seller=seller, current_price=current_price)
            new_listing.save()

            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": new_listing.id}))
    else:
        return render(request, 'auctions/new_listing.html', {
            'form': ListingForm()
        })


def listing(request, listing_id, good_bid=1):
    current_listing = AuctionListing.objects.get(pk=listing_id)
    watching = request.user in current_listing.watchlist.all()
    return render(request, "auctions/listing.html", {
        "listing": current_listing,
        "watching": watching,
        "bidding_form": BiddingForm(),
        "comment_form": CommentForm(),
        "comments": current_listing.comments.all(),
        "good_bid": good_bid
    })


def toggle_watchlist(request, listing_id):
    if request.method == 'POST':
        current_listing = AuctionListing.objects.get(pk=listing_id)

        if request.user in current_listing.watchlist.all():
            current_listing.watchlist.remove(request.user)
        else:
            current_listing.watchlist.add(request.user)    

    return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))


def create_bid(request, listing_id):
    if request.method == 'POST':
        current_listing = AuctionListing.objects.get(pk=listing_id)
        new_bid = int(request.POST['new_bid'])

        if new_bid >= current_listing.starting_bid and new_bid > int(current_listing.current_price.bid):
            valid_bid = Bid(bid=new_bid, bidder=request.user)
            valid_bid.save()
            current_listing.current_price = valid_bid
            current_listing.save()
        else:
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id, "good_bid": 0}))

    return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id, "good_bid": 2}))


def close_bid(request, listing_id):
    if request.method == 'POST':
        current_listing = AuctionListing.objects.get(pk=listing_id)
        current_listing.active = False
        current_listing.save()
    return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))


def comment(request, listing_id):
    if request.method == 'POST':
        current_listing = AuctionListing.objects.get(pk=listing_id)
        new_comment = Comment(author=request.user, message=request.POST['message'])
        new_comment.save()
        current_listing.comments.add(new_comment)
    return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))


def watchlist(request):
    avail_listings = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "avail_listings": avail_listings
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
