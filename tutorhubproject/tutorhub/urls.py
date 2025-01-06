from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


urlpatterns = [
    # Authentication
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path('favicon.ico', RedirectView.as_view(url='/static/tutorhub/images/mentor-logo-bull.svg', permanent=True)),
    
    # default route
    path("", views.index, name="index"),

    # Following
    path("follow/<int:tutor_id>/", views.follow_tutor, name="follow_tutor"),

    # User profile endpoints
    path('profile/<int:user_id>/', views.profile, name='profile'),
    path('my-profile/', views.profile, name='my_profile'),
    path('remove_profile_image/', views.remove_profile_image, name='remove_profile_image'),
    path('delete_credential/<int:credential_id>/', views.delete_credential, name='delete_credential'),
    path('delete_subject_level/<int:subject_level_id>/', views.delete_subject_level, name='delete_subject_level'),


    # Messaging
    path('messages/', views.messages, name='messages'),
    path("unread_messages_count/", views.unread_messages_count, name="unread_messages_count"),
    path('edit_message/<int:message_id>/', views.edit_message, name='edit_message'),

    path('follow/<int:tutor_id>/', views.follow_tutor, name='follow_tutor'),
    path('followed/', views.followed_tutors, name='followed_tutors'),
]

# For image uploading 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)