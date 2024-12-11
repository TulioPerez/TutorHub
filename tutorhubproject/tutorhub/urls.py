from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # default route
    path("", views.index, name="index"),

    # authentication
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # Profile management
    path('profile/<int:user_id>/', views.profile, name='profile'),  # View another user's profile
    path('my-profile/', views.profile, name='my_profile'),  # View your profile
path('edit-profile/', views.edit_profile, name='edit_profile'),

    path('search/', views.search_tutors, name='search_tutors'),
    path('messages/', views.message_list, name='message_list'),
    path('message/<int:receiver_id>/', views.send_message, name='send_message'),
    path('like/<int:tutor_id>/', views.like_tutor, name='like_tutor'),
    path('liked/', views.liked_tutors, name='liked_tutors'),
]

# For image uploading 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)