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

    # View a user's profile
    path('profile/<int:user_id>/', views.profile, name='profile'),

    # View & edit one's own profile
    path('my-profile/', views.profile, name='my_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('delete_credential/<int:credential_id>/', views.delete_credential, name='delete_credential'),

    # Messaging
    # path('messages/', views.messages, name='messages'),
    path('edit_message/<int:message_id>/', views.edit_message, name='edit_message'),

    path('like/<int:tutor_id>/', views.like_tutor, name='like_tutor'),
    path('liked/', views.liked_tutors, name='liked_tutors'),

    path('search/', views.search_tutors, name='search_tutors'),
]

# For image uploading 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)