from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, AuctionListing
from .forms import ListingForm


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
            auction_listing = AuctionListing(title=title, description=description, starting_bid=starting_bid, image=image, category=category, seller=seller)
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
    item = AuctionListing.objects.get(pk=listing_id)
    if request.method == 'POST':
        if watching:
            request.user.watchlist.remove(item)
            watching = not watching
        else:
            request.user.watchlist.add(item)
            watching = not watching
    else:
        if request.user.is_authenticated:
            watching = (item in request.user.watchlist.all())
    return render(request, "auctions/listing.html", {
        "listing": item,
        "watching": int(watching)
    })


def watchlist(request):
    """
    Display all of the listings that a user has added to their watchlist.
    Clicking on any of those listings should take the user to that listing's page.
    """
    auction_listings = AuctionListing.objects.all()
    return render(request, "auctions/index.html", {
        "auction_listings": auction_listings
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
