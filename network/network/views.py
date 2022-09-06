from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core import serializers

from .models import Post, User, UserFollowing

class NewPostForm(forms.Form):
    post = forms.CharField(label='', widget=forms.Textarea(attrs={"class" : "form", "id" : "post"}))

class EditForm(forms.Form):
    def __init__(self, *args, **kwargs):
        post = kwargs.pop('post')
        super(EditForm, self).__init__(*args, **kwargs)
        self.fields['content'] = forms.CharField(label = '', widget=forms.Textarea({
            'id' : 'post',
            'class' : 'form',
        }), initial = post)



def index(request):
    if request.method == "POST":
        post = NewPostForm(request.POST)
        if post.is_valid():
            body = post.cleaned_data["post"]
            newpost = Post(poster=request.user, body=body)
            newpost.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "network/index.html",{
                "form" : post
            })
    else:
        posts = Post.objects.all().order_by("-date")
        p = Paginator(posts, 10)
        c = p.num_pages
        previous = 1
        if request.GET.get("page", None) == None:
            p = p.page(1)
            next = 2
            current = 1
        else:
            x = int(request.GET['page'])
            p = p.page(x)
            current = x
            next = x + 1
            if x > 1:
                previous = x - 1
        
        return render(request, "network/index.html", {
            "form" : NewPostForm(),
            "posts" : p,
            "c" : c,
            "c_list" : range(1, c+1),
            "next" : next,
            "previous" : previous,
            "current" : current
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, profile):
    userP = User.objects.filter(username=profile)
    userP = userP[0]
    followers = UserFollowing.objects.filter(followee = userP)
    followees = UserFollowing.objects.filter(follower = userP)
    x = len(followers)
    y = len(followees)
    following = None
    for follower in followers:
        if request.user == follower.follower:
            following = True
            break
        else:
            following = False

    posts = Post.objects.filter(poster = userP).order_by("-date")
    p = Paginator(posts, 10)
    c = p.num_pages
    previous = 1
    if request.GET.get("page", None) == None:
        p = p.page(1)
        next = 2
        current = 1
    else:
        x = int(request.GET['page'])
        p = p.page(x)
        current = x
        next = x + 1
        if x > 1:
            previous = x - 1
    return render(request, "network/profile.html",{
        "profile" : userP,
        "followers" : followers,
        "x" : x,
        "y" : y,
        "following" : following,
        "posts" : p,
        "c" : c,
        "c_list" : range(1, c+1),
        "next" : next,
        "previous" : previous,
        "current" : current
    })

@login_required
def follow(request):
    if request.method == "POST":
        data = json.loads(request.body)
        profile = data['profile']
        userP = User.objects.filter(username=profile)
        userP = userP[0]
        if data['unfollow'] == True:
            following = UserFollowing.objects.filter(follower=request.user, followee=userP)
            following.delete()
            return JsonResponse({'status': 201}, status=201)
        else:
            new_following = UserFollowing(follower=request.user, followee=userP)
            new_following.save()
            return JsonResponse({'status': 201}, status=201)
    else:
        return HttpResponse(status=404)

@login_required
def following(request):
    followees = UserFollowing.objects.filter(follower=request.user)
    usersF = []
    for followee in followees:
        userF = followee.followee
        usersF.append(userF)
    all_posts = []
    for userF in usersF:
        posts = Post.objects.filter(poster=userF).order_by("-date")
        for post in posts:
            all_posts.append(post)
    all_posts.sort(key= lambda i: i.date, reverse=True)
    p = Paginator(all_posts, 10)
    c = p.num_pages
    previous = 1
    if request.GET.get("page", None) == None:
        p = p.page(1)
        next = 2
        current = 1
    else:
        x = int(request.GET['page'])
        p = p.page(x)
        current = x
        next = x + 1
        if x > 1:
            previous = x - 1
    return render(request, "network/follow.html", {
        "posts" : p,
        "c" : c,
        "c_list" : range(1, c+1),
        "next" : next,
        "previous" : previous,
        "current" : current
    })

@login_required
def edit(request):
    id = request.GET.get('post')
    post = Post.objects.filter(id=id)
    post=post[0]
    if request.user == post.poster:
        if request.method == "POST":
            body = EditForm(request.POST, post=request.POST['content'])
            if body.is_valid():
                body = body.cleaned_data['content']
                post.body = body
                post.save()
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "network/edit.html", {
                    "post" : post,
                    'form' : body
                })
        else:
            id = request.GET.get('post')
            post = Post.objects.filter(id=id)
            post=post[0]
            return render(request, "network/edit.html", {
                "post" : post,
                'form' : EditForm(post=post.body)
            })
    else:
            return HttpResponse(status=403)

def like(request):
    if request.method == "POST":
        data = json.loads(request.body)
        post = data['post']
        postP = Post.objects.filter(id=post)
        postP = postP[0]
        if data['unlike'] == True:
            postP.likes.remove(request.user)
            postP.like_num = postP.like_num - 1
            postP.save()
            return JsonResponse({'status': 201}, status=201)
        else:
            postP.likes.add(request.user)
            postP.like_num = postP.like_num + 1
            postP.save()
            return JsonResponse({'status': 201}, status=201)
    else:
        return HttpResponse(status=404)