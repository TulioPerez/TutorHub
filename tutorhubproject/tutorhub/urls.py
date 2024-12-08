from django.urls import path
from . import views

urlpatterns = [
    # default route
    path("", views.index, name="index"),

    # authentication
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # pages & functions
    path('profile/<int:user_id>/', views.profile, name='profile'),

    path('my-profile/', views.my_profile, name='my_profile'),

    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('edit-tutor-details/', views.edit_tutor_details, name='edit_tutor_details'),

    path('search/', views.search_tutors, name='search_tutors'),
    path('messages/', views.message_list, name='message_list'),
    path('message/<int:receiver_id>/', views.send_message, name='send_message'),
    path('like/<int:tutor_id>/', views.like_tutor, name='like_tutor'),
    path('liked/', views.liked_tutors, name='liked_tutors'),
]
