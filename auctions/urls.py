from django.urls import path




from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("all", views.all, name="all"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("create", views.create, name="create"),
    path("catagories/<int:catagory_id>", views.catagories, name="catagories"),
    path("close/<int:listing_id>", views.close, name="close"),
    path("listings/<int:listing_id>", views.listing, name="listing"),
    path("listings/<int:listing_id>/edit", views.edit, name="edit"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("<int:listing_id>/watchlist/add", views.add_watchlist, name="add_watchlist"),
    path("<int:listing_id>/watchlist/remove", views.remove_watchlist, name="remove_watchlist"),
    path("<int:listing_id>/comment", views.comment, name="comment"),
]
