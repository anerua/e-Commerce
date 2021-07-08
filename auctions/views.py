from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User


def index(request):
    """
    Let users view all the currently active auction listings.
    For each active listing, this page should display (at minimum)
    the title, description, current price, and photo (if one exists for the listing)
    """
    return render(request, "auctions/index.html")


def categories(request):
    # List all the categories. Clicking on the name of any category
    # should take the user to a page that displays all fo the active listings
    # in that category
    return render(request, "auctions/index.html")


def create_listing(request):
    # Form to create a listing. Specify title, text-based description, and starting bid.
    # Optionally can provide a URL for an image for the listing
    # and/or a category (e.g. Fashion, Toys, Electronics, Home, etc)
    return render(request, "auctions/index.html")


def listing(request):
    """
    Users should be able to view all details about the listing, including current listing price
    """
    return render(request, "auctions/index.html")


def watchlist(request):
    """
    Display all of the listings that a user has added to their watchlist.
    Clicking on any of those listings should take the user to that listing's page.
    """
    return render(request, "auctions/index.html")


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
