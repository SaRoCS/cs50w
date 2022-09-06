from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    pass

class Post(models.Model):
    body = models.TextField(blank=True)
    poster = models.ForeignKey(User, on_delete=CASCADE, related_name="posts")
    date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="likes")
    like_num = models.IntegerField(default=0)

class UserFollowing(models.Model):
    follower = models.ForeignKey(User, on_delete=CASCADE, related_name="followee")
    followee = models.ForeignKey(User, on_delete=CASCADE, related_name="follower")


