from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, AuctionListing, Bid, Comment
from .forms import ListingForm, BiddingForm, CommentForm


def index(request):
    """
    Let users view all the currently active auction listings.
    For each active listing, this page should display (at minimum)
    the title, description, current price, and photo (if one exists for the listing)
    """
    auction_listings = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {
        "auction_listings": auction_listings
    })


def categories(request):
    avail_categories = AuctionListing.objects.values_list('category', flat=True).distinct().order_by()
    return render(request, "auctions/categories.html", {
        "categories": avail_categories
    })


def category_listing(request, category):
    avail_listings = AuctionListing.objects.filter(category=category)
    return render(request, "auctions/category_listing.html", {
        "category": category,
        "avail_listings": avail_listings
    })


@login_required(login_url='auctions/login.html')
def create_listing(request):
    # Form to create a listing. Specify title, text-based description, and starting bid.
    # Optionally can provide a URL for an image for the listing
    # and/or a category (e.g. Fashion, Toys, Electronics, Home, etc)
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
            auction_listing = AuctionListing(title=title, description=description, starting_bid=starting_bid, image=image, category=category, seller=seller, current_price=current_price)
            auction_listing.save()
            auction_listings = AuctionListing.objects.all()
            return render(request, "auctions/index.html", {
                "auction_listings": auction_listings
            })
    else:
        form = ListingForm()
    return render(request, 'auctions/new_listing.html', {
        'form': form
    })

    auction_listings = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {
        "auction_listings": auction_listings
    })


def listing(request, listing_id, watching=0):
    """
    Users should be able to view all details about the listing, including current listing price
    """
    current_listing = AuctionListing.objects.get(pk=listing_id)
    if request.method == 'POST':
        if watching:
            request.user.watchlist.remove(current_listing)
            watching = not watching
        else:
            request.user.watchlist.add(current_listing)
            watching = not watching
    else:
        if request.user.is_authenticated:
            watching = (current_listing in request.user.watchlist.all())
    return render(request, "auctions/listing.html", {
        "listing": current_listing,
        "watching": int(watching),
        "bidding_form": BiddingForm(),
        "comment_form": CommentForm(),
        "comments": current_listing.comments.all(),
        "error_bid": False
    })


def create_bid(request, listing_id):
    current_listing = AuctionListing.objects.get(pk=listing_id)
    watching = (current_listing in request.user.watchlist.all())
    error_bid = False
    if request.method == 'POST':
        new_bid = int(request.POST['new_bid'])
        if new_bid >= current_listing.starting_bid and new_bid > int(current_listing.current_price.bid):
            # create bid
            valid_bid = Bid(bid=new_bid, bidder=request.user)
            valid_bid.save()
            current_listing.current_price = valid_bid
            current_listing.save()
        else:
            error_bid = True

    return render(request, "auctions/listing.html", {
        "listing": current_listing,
        "watching": int(watching),
        "bidding_form": BiddingForm(),
        "comment_form": CommentForm(),
        "comments": current_listing.comments.all(),
        "error_bid": error_bid
    })


def close_bid(request, listing_id):
    current_listing = AuctionListing.objects.get(pk=listing_id)
    watching = (current_listing in request.user.watchlist.all())
    if request.method == 'POST':
        current_listing.active = False
        current_listing.save()

    return render(request, "auctions/listing.html", {
        "listing": current_listing,
        "watching": int(watching),
        "bidding_form": BiddingForm(),
        "comment_form": CommentForm(),
        "comments": current_listing.comments.all(),
        "error_bid": False
    })        


def comment(request, listing_id):
    current_listing = AuctionListing.objects.get(pk=listing_id)
    watching = (current_listing in request.user.watchlist.all())
    if request.method == 'POST':
        new_comment = Comment(author=request.user, message=request.POST['message'])
        new_comment.save()
        current_listing.comments.add(new_comment)

    return render(request, "auctions/listing.html", {
        "listing": current_listing,
        "watching": int(watching),
        "bidding_form": BiddingForm(),
        "comment_form": CommentForm(),
        "comments": current_listing.comments.all(),
        "error_bid": False
    })        


def watchlist(request):
    """
    Display all of the listings that a user has added to their watchlist.
    Clicking on any of those listings should take the user to that listing's page.
    """
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
