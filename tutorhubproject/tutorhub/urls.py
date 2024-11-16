from django.urls import path
from . import views

urlpatterns = [
    # default routes
    path("", views.index, name="index"),

    # authentication routes
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # page routes
]