from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name='create'),
    path("listing/<str:title>", views.listing_view, name='listing'),
    path("close/<str:title>", views.close, name='close'),
    path("watch/<str:title>", views.watch, name='watch'),
    path("unwatch/<str:title>", views.unwatch, name='unwatch'),
    path("comment/<str:title>", views.comment_func, name='comment'),
    path("watchlist", views.watchlist, name='watchlist'),
    path('category/<str:category>', views.category_view, name='category'),
    path('categories', views.category_list, name='category_list')
]
