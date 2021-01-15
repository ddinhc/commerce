from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import Max


from .models import *

class NewListingForm(forms.Form):
    CATEGORIES = Catagory.objects.all().values_list("id", "tag")
    title = forms.CharField(label="Title",widget=forms.TextInput(attrs={"class": "form-control"}))
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={"class": "form-control", "row": 5}), required=False)
    catagory = forms.MultipleChoiceField(label="Catagory", required=False, widget=forms.SelectMultiple(attrs={"class": "form-control"}), choices=CATEGORIES)
    price = forms.DecimalField(label="Price", max_digits=7,decimal_places=2, widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "00.00"}))
    image = forms.ImageField(required=False)
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)


def index(request):
    active_listings = Listing.objects.filter(active=True)

    return render(request, "auctions/index.html", {
        "listings": active_listings,
        "active_listing": True,
    })

def all(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings,
        "active_listing": False,
    })

def catagories(request, catagory_id):

    try:
        catagory = Catagory.objects.get(pk=catagory_id)
    except Catagory.DoesNotExist:
        catagory = None
    if catagory is None:
        catagories = Catagory.objects.all()
        return render(request, "auctions/catagories.html", {
            "catagories": catagories,
        })
    else:
        cat_listings = Listing.objects.filter(catagory=catagory)
        return render(request, "auctions/index.html", {
            "listings": cat_listings,
            "catagory": catagory.tag,
            "cat_filter": True
        })

@login_required(login_url="auctions:login")
def create(request):

    if request.method == "POST":
        form = NewListingForm(request.POST, request.FILES)
        user = request.user

        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            price = form.cleaned_data["price"]
            image = form.cleaned_data["image"]
            catagories = form.cleaned_data["catagory"]

            try:
               listing = Listing.objects.get(title=title)
            except Listing.DoesNotExist:
                listing = None

            if  listing is None and form.cleaned_data["edit"] is False:

                new_listing = Listing.objects.create(title=title, description=description, price=price, image=image, user=user, active=True)
                new_listing.catagory.set(catagories)
                new_listing.save()
                return HttpResponseRedirect(reverse("auctions:listing", args=(new_listing.id,)))
            elif form.cleaned_data["edit"] is True:

                if image is not None:
                    listing_with_image = get_object_or_404(Listing, title=title)
                    listing_with_image.image = image
                    listing_with_image.save()
                if catagories is not None:
                    listing_with_cat = get_object_or_404(Listing, title=title)
                    listing_with_cat.catagory.set(catagories)
                    listing_with_cat.save()

                existing_listing = Listing.objects.filter(title=title)
                existing_id = Listing.objects.get(title=title).id

                existing_listing.update(title=title, description=description, price=price)
                return HttpResponseRedirect(reverse("auctions:listing", args=(existing_id,)))
            else:
                return render(request, "auctions/create.html", {
                    "form": form,
                    "error": "Duplicate Item.",
                    "existing_title": title,
                    "existing_id": listing.id,
                })
        else:
            return render(request, "auctions/create.html", {
            "form": NewListingForm()
            })

    else:
        return render(request, "auctions/create.html", {
            "form": NewListingForm()
        })

@login_required(login_url="auctions:login")       
def close(request, listing_id):
    user = request.user
    try:
        listing_to_close = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        listing_to_close = None
    if listing_to_close is None:
        return render(request, "auctions/index.html", {
            "error": "Invalid Listing."
        })
    else:
        if user == listing_to_close.user:
            listing_to_close.active = False
            listing_to_close.save()
            return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))
        else:
            return render(request, "acutions/listing.html", {
                "listing": listing_to_close,
                "error": "Invalid Request",
            })

def profile(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        user = None
    if user:
        return render(request, "auctions/profile.html", {
            "user": user,
        })
    else:
        return render(request, "auctions/index.html", {
            "error": "Invalid User."
        })

@login_required(login_url="auctions:login")
def edit(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        listing = None
    if listing is None:
        return render(request, "auctions/index.html", {
            "error": "Invalid Access."
        })
    else:
        form = NewListingForm()
        CATEGORIES = listing.catagory.all()
        form.fields["edit"].initial = True
        form.fields["title"].initial = listing.title
        form.fields["description"].initial = listing.description
        form.fields["price"].initial = listing.price
        form.fields["image"].initial = listing.image
        form.initial["catagory"] = [cat.pk for cat in CATEGORIES]
        return render(request, "auctions/create.html", {
            "form": form,
            "edit": form.fields["edit"].initial,
        })

@login_required(login_url="auctions:login")
def bid(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        amount = request.POST["amount"]
        bid_listing = Bid.objects.filter(listing=listing)
        value = bid_listing.aggregate(Max("amount"))["amount__max"]
        user = request.user
        comments = Comment.objects.filter(listing=listing)
        if value is None:
            value = 0
        if float(amount) < listing.price or float(amount) <= value:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "error": f"Bid needs to be higher than ${max(round(value, 2), listing.price)}!",
                "current_amount": value,
                "bids": bid_listing,
                "comments": comments,
            })
        else:
            bid = Bid.objects.create(user=user, listing=listing, amount=amount)
            bid.save()
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "current_text": f"{bid_listing.count()} bid(s) so far. Your bid is the current bid. ",
                "current_amount": bid.amount,
                "comments": comments,
            })

    else:
        return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))

@login_required(login_url="auctions:login")
def watchlist(request):
    user = request.user
    listings = user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })

@login_required(login_url="auctions:login")
def add_watchlist(request, listing_id):
    user = request.user
    try:
        listing_to_add = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        listing_to_add = None

    if listing_to_add is not None:
        user.watchlist.add(listing_to_add)
        user.save()
        return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))
    else:
        return render(request, "auctions/watchlist.html", {
            "error": "Invalid request."
        })

@login_required(login_url="acutions:login")
def remove_watchlist(request, listing_id):
    user = request.user
    try:
        listing_to_remove = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        listing_to_remove = None
    if listing_to_remove is not None:
        user.watchlist.remove(listing_to_remove)
        user.save()
        return HttpResponseRedirect(reverse("auctions:listing", args=(listing_id,)))
    else:
        return render(request, "auctions/watchlist.html", {
            "error": "Invalid request."
        })

@login_required(login_url="auctions:login")
def listing(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)

    except Listing.DoesNotExist:
        listing = None
    if listing is None:
        return render(request, "auctions/index.html", {
            "error": "Invalid Listing Request."
        })
    catagories = listing.catagory.all()
    comments = Comment.objects.filter(listing=listing)
    user = request.user
    watchlist_on = False
    bids = Bid.objects.filter(listing=listing)
    value = bids.aggregate(Max("amount"))["amount__max"]
    win_bid = None
    current_amount = bids.aggregate(Max("amount"))["amount__max"]
    if value is not None:
        win_bid = Bid.objects.filter(amount=value)[0]
    if listing in user.watchlist.all():
        watchlist_on = True

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlist_on": watchlist_on,
        "win_bid": win_bid,
        "bids": bids,
        "current_amount": current_amount,
        "catagories": catagories,
        "comments": comments,
    })

def comment(request, listing_id):
    if request.method == "POST":
        try:
            listing = Listing.objects.get(pk=listing_id)
        except Listing.DoesNotExist:
            listing = None
        if listing is None:
            return render(request, "auctions/index.html", {
                "error": "Invalid Access"
            })
        else:
            user = request.user
            comments = Comment.objects.filter(listing=listing)
            text = request.POST["comment"]
            comment = Comment.objects.create(user=user, listing=listing, text=text)
            comment.save()
            
            
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
            })
    else: 
        return HttpResponseRedirect(reveres("auctions:listing", args=(listing_id,)))
        



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


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
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")
