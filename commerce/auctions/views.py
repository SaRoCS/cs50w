from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required


from .models import *

categories = [("Clothing, Shoes, Jewelry & Watches",'Clothing, Shoes, Jewelry & Watches'),
    ("Books",'Books'),
    ("Movies, Music & Games",'Movies, Music & Games'),
    ("Electronics",'Electronics'),
    ("Home, Garden & Tools",'Home, Garden & Tools'),
    ("Toys",'Toys'),
    ("Handmade",'Handmade'),
    ("Sports",'Sports'),
    ("Outdoors",'Outdoors')]

class ListingForm(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    description = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Description'}))
    price = forms.IntegerField(label='', min_value=0, max_value=99999.99, widget=forms.NumberInput(attrs={'placeholder':"Starting Bid"}))
    image = forms.URLField(label='', required=False, widget=forms.TextInput(attrs={'placeholder': 'URL For Image Optional'}))
    category = forms.MultipleChoiceField(choices=categories,label='Category (Optional)', required=False, widget=forms.CheckboxSelectMultiple())

class BidForm(forms.Form):
    def __init__(self, *args, **kwargs):
        minimum = kwargs.pop('minimum')
        super(BidForm, self).__init__(*args, **kwargs)
        self.fields['bid'] = forms.DecimalField(label= '',decimal_places=2, max_value=99999.99, min_value = minimum + 1.00, widget=forms.NumberInput(attrs={'placeholder':"Bid"}))
class CommentForm(forms.Form):
    comment = forms.CharField(label='', widget=forms.Textarea(attrs={'placeholder' : 'Comment'}))


def index(request):
    listings = Listing.objects.filter(is_active=True)
    for listing in listings:
        categoryUn = listing.category
        category = list(categoryUn.split("$"))
        category.pop(0)
        listing.category = category

        priceUn = listing.price
        price = '$' + str(priceUn)
        listing.price = price    
    return render(request, "auctions/index.html",{
        "listings" : listings
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
def create(request):
    if request.method == "POST":
        listing = ListingForm(request.POST)
        if listing.is_valid():
            #get form data
            title = listing.cleaned_data['title']
            title = title.capitalize()
            description = listing.cleaned_data['description']
            price = listing.cleaned_data['price']
            image = listing.cleaned_data['image']
            categorylist = listing.cleaned_data['category']
            category=''
            for c in categorylist:
                category += "$" + c

            #store data
            username = request.user.username
            user = User.objects.get(username=username)
            listing = Listing(price=price, title=title, description=description, image=image, category=category, lister=user)
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/create.html",{
                'form' : listing
            })
        return 
    else:
        return render(request, "auctions/create.html",{
            "form" : ListingForm()
        })

def listing_view(request, title):
    listing = Listing.objects.filter(title=title.capitalize())
    minimum = float(listing[0].price)
    high = listing[0].bids.all()
    comments = list(Comment.objects.filter(listing=listing[0]))
    comments.reverse()

    categoryUn = listing[0].category
    category = list(categoryUn.split("$"))
    category.pop(0)
    if high:
        high.order_by("-value")
        high = high[0]
        high = high.bidder
    if request.method == "POST":
        bidF = BidForm(request.POST, minimum=minimum)
        if bidF.is_valid():
            bid = bidF.cleaned_data['bid']
            newBid = Bid(value=bid, bidder=request.user, listing=listing[0])
            newBid.save()
            listing.update(price=bid)
            request.user.watch_item.add(listing[0])
            return HttpResponseRedirect(reverse("listing", kwargs={
                "title" : title
            }))
        else:
            return render(request, "auctions/listing.html",{
                "listing" : listing[0],
                "form" : bidF,
                "watch" :watch,
                "high" : high,
                "comment" : CommentForm(),
                'comments' : comments,
                'category' : category
            })
    else:
        form = BidForm(minimum=minimum)
        return render(request, "auctions/listing.html",{
            "listing" : listing[0],
            "form" : form,
            "watch" : watch,
            'high' : high,
            'comment' : CommentForm(),
            'comments' : comments,
            'category' : category
        })

@login_required
def close(request, title):
    listing = Listing.objects.filter(title=title)
    listing.update(is_active=False)
    return HttpResponseRedirect(reverse("listing", kwargs={'title':title}))

@login_required
def watch(request, title):
    listing = Listing.objects.filter(title=title)
    request.user.watch_item.add(listing[0])
    return HttpResponseRedirect(reverse("listing", kwargs={'title':title}))

@login_required
def unwatch(request, title):
    listing = Listing.objects.filter(title=title)
    request.user.watch_item.remove(listing[0])
    return HttpResponseRedirect(reverse("listing", kwargs={'title':title}))

@login_required
def comment_func(request, title):
    if request.method == "POST":
        commentf = CommentForm(request.POST)
        if commentf.is_valid():
            comment = commentf.cleaned_data['comment']
            listing = Listing.objects.filter(title=title)
            c = Comment(comment=comment, commenter=request.user, listing=listing[0])
            c.save()
            return HttpResponseRedirect(reverse('listing', kwargs={'title':title}))
        else:
            return HttpResponseRedirect(reverse('listing', kwargs={'title':title}))
    else:
        return HttpResponseNotFound()

@login_required
def watchlist(request):
    wlist = request.user.watch_item.all()
    for listing in wlist:
        categoryUn = listing.category
        category = list(categoryUn.split("$"))
        category.pop(0)
        listing.category = category

        priceUn = listing.price
        price = '$' + str(priceUn)
        listing.price = price    
    return render(request, "auctions/watchlist.html",{
        "wlist" : wlist
    })

def category_view(request, category):
    listings = Listing.objects.filter(category__regex=f".*{category}.*")
    #if listings:
    for listing in listings:
        categoryUn = listing.category
        category = list(categoryUn.split("$"))
        category.pop(0)
        listing.category = category

        priceUn = listing.price
        price = '$' + str(priceUn)
        listing.price = price    
    return render(request, "auctions/category.html",{
        "listings" : listings
    })
    
def category_list(request):
    return render(request, "auctions/category_list.html",{
        "categories" : categories
    })