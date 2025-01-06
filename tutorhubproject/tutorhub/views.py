from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Level, User, Message, SubjectLevel, Credential, Address
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.timezone import now
from django_countries import countries
from django.utils.safestring import mark_safe
import json


# ***************************
# ***** Templates Views *****
# ***************************


def index(request):
    query = request.GET.get('q', '').strip()
    view_type = request.GET.get('view', 'all')
    subject_levels_prefetch = Prefetch(
        'tutor_subject_levels',
        queryset=SubjectLevel.objects.all()
    )
    tutors = User.objects.filter(is_tutor=True).prefetch_related(subject_levels_prefetch).order_by('nickname', 'first_name', 'username')

    # Search Functionality
    if view_type == "search" and query:
        tutors = tutors.filter(
            Q(nickname__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(address__street_address__icontains=query) |
            Q(address__city__icontains=query) |
            Q(address__postal_code__icontains=query) |
            Q(address__state_region__icontains=query)
            # Q(subject_levels__subject__icontains=query)
            # TODO ADD SEARCH FILTERS: by name, city, state, subject, level, bio content
        ).distinct()


    # Handle following listing
    if view_type == "following" and request.user.is_authenticated:
        tutors = request.user.followed_tutors.all()

    # Pagination
    page_obj = paginate_queryset(tutors, request.GET.get('page'))

    # Determine page title
    if view_type == "search":
        page_title = "Search Results"
    elif view_type == "following":
        page_title = "Following"
    else:
        page_title = "All Tutors"

    return render(request, 'tutorhub/index.html', {
        'page_obj': page_obj,
        'page_title': page_title,
        'view_type': view_type,
    })


# ************************************
# ********** LOGIN - LOGOUT **********
# ************************************


# Authentication
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "tutorhub/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "tutorhub/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# ******************************
# ********** REGISTER **********
# ******************************

def register(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        user_type = request.POST.get("user_type")

        if password != confirmation:
            return render(request, "tutorhub/register.html", {
                "message": "Passwords must match."
            })

        # Create a new user
        try:
            user = User.objects.create_user(email, email, password)
            user.nickname = request.POST.get("nickname", "")
            user.first_name = request.POST.get("first_name", "")
            user.last_name = request.POST.get("last_name", "")
            user.is_tutor = (user_type == "tutor")

            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "tutorhub/register.html", {
                "message": "Email address already taken."
            })


        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    return render(request, "tutorhub/register.html", {
    })

# *****************************
# ********** PROFILE **********
# *****************************

# todo not needed for profile completion: birthdate

@login_required
def profile(request, user_id=None):
    profile_user = request.user if user_id is None else get_object_or_404(User, id=user_id)

    # Handle profile updating
    if request.method == "POST" and profile_user == request.user:

        # Nickname & Bio (first, last cannot be changed)
        profile_user.nickname = request.POST.get('nickname', '')
        profile_user.middle_name = request.POST.get('middle_name', '')
        profile_user.bio = request.POST.get('bio', '')
        profile_user.birthdate = request.POST.get('birthdate', None)
        profile_user.phone_number = request.POST.get('phone_number', None)
        profile_user.email = request.POST.get('email', profile_user.email)
        
        # Handle alerts for missing profile data alerts 
        profile_user.missing_profile_data_alert = request.POST.get('missing_profile_data_alert') == 'on'

        # Handle profile data visibility toggling
        profile_user.show_full_name = 'show_full_name' in request.POST
        profile_user.show_birthdate = 'show_birthdate' in request.POST
        profile_user.show_phone_number = 'show_phone_number' in request.POST
        profile_user.show_email = 'show_email' in request.POST
        profile_user.show_address = 'show_address' in request.POST
        profile_user.missing_profile_data_alert = 'missing_profile_data_alert' in request.POST

        # Profile image
        if 'profile_image' in request.FILES:
            profile_user.profile_image = request.FILES['profile_image']

        # Address
        if not profile_user.address:
            profile_user.address = Address.objects.create()
        profile_user.address.street_address = request.POST.get('street_address', '')
        profile_user.address.city = request.POST.get('city', '')
        profile_user.address.state_region = request.POST.get('state', '')
        profile_user.address.postal_code = request.POST.get('postal_code', '')
        profile_user.address.country = request.POST.get('country', '')
        profile_user.address.save()

        # Availability
        availability_days = request.POST.getlist('availability_days[]')
        availability_start = request.POST.getlist('availability_start[]')
        availability_end = request.POST.getlist('availability_end[]')

        availability = []
        for day, start, end in zip(availability_days, availability_start, availability_end):
            availability.append({
                'day': day,
                'start': start,
                'end': end
            })
        profile_user.availability = availability

        # Subjects & levels
        subjects = request.POST.getlist("subjects[]")
        for index, subject in enumerate(subjects):
            if subject.strip():
                selected_levels = request.POST.getlist(f"levels_{index}[]")

                # Ensure levels are unique
                unique_levels = list(set(selected_levels))  

                if unique_levels:
                    # Update or create a single entry for the subject with multiple levels
                    SubjectLevel.objects.update_or_create(
                        tutor=profile_user,
                        subject=subject.strip(),
                        defaults={"levels": unique_levels},  # Store levels
                    )


        # Credentials
        if 'credentials[]' in request.FILES:
            for file in request.FILES.getlist('credentials[]'):
                Credential.objects.create(user=profile_user, file=file)

        profile_user.save()
        return JsonResponse({"success": True, "message": "Profile updated successfully."})

    # Display profile logic (profile functionality)
    credentials = profile_user.credentials.all()

    # Retrieve levels from the TextChoices class
    levels = [{'value': value, 'display': display} for value, display in Level.choices]
    levels_json = mark_safe(json.dumps(levels))

    day_order = {
        "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
        "Friday": 4, "Saturday": 5, "Sunday": 6
    }
    availability = profile_user.availability
    sorted_availability = sorted(
        availability,
        key=lambda slot: (day_order.get(slot['day'], 7), slot['start'])
    )

    # For alerting user about missing profile data
    missing_details_list = []

    if not profile_user.nickname:
        missing_details_list.append("Nickname")

    if not profile_user.bio:
        missing_details_list.append("Bio")

    if not profile_user.credentials.exists():
        missing_details_list.append("Credentials")

    if not profile_user.profile_image:
        missing_details_list.append("Profile Image")

    if not profile_user.address or not all([
        profile_user.address.street_address,
        profile_user.address.city,
        profile_user.address.state_region,
        profile_user.address.country
        # profile_user.address.postal_code,
    ]):
        missing_details_list.append("Complete Address (Street Address, City, State, and Country)")

    if not profile_user.availability:
        missing_details_list.append("Availability")

    if not SubjectLevel.objects.filter(tutor=profile_user).exists():
        missing_details_list.append("Subjects and Levels")

    messages = Message.objects.filter(
        (Q(sender=request.user, receiver=profile_user) | Q(sender=profile_user, receiver=request.user))
    ).order_by('timestamp')

    scroll_to = request.GET.get('scroll_to')
    if scroll_to:
        try:
            message_to_mark = messages.get(id=scroll_to, receiver=request.user, read=False)
            message_to_mark.read = True
            message_to_mark.save()
        except Message.DoesNotExist:
            pass

    countries_list = list(countries)
    for credential in credentials:
        credential.is_image = credential.file.url.lower().endswith(('.jpg', '.jpeg', '.png'))

    display_name = profile_user.nickname or profile_user.first_name or "User"
    possessive_name = f"{display_name}'s" if not display_name.endswith('s') else f"{display_name}'"
    subject_levels = SubjectLevel.objects.filter(tutor=profile_user)

    return render(request, 'tutorhub/profile.html', {
        'profile': profile_user,
        'is_own_profile': profile_user == request.user,
        'credentials': credentials,
        'days_of_week': list(day_order.keys()),
        "subject_levels": subject_levels,
        "levels": levels,
        "levels_json": levels_json,
        'countries': countries_list,
        'messages': messages,
        'scroll_to': scroll_to,
        'missing_details': missing_details_list,
        'possessive_name': possessive_name,
        'sorted_availability': sorted_availability,
    })


# *****************************
# ***** Template Handling *****
# *****************************


@login_required
def remove_profile_image(request):
    if request.method == "POST":
        user = request.user
        if user.profile_image:
            # Delete the image file
            user.profile_image.delete()
            user.profile_image = None
            user.save()
            return JsonResponse({"success": True, "message": "Profile image removed successfully."})
        return JsonResponse({"success": False, "error": "No profile image to remove."}, status=400)
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)


@login_required
def delete_credential(request, credential_id):
    try:
        credential = Credential.objects.get(id=credential_id, user=request.user)
        credential.delete()
        return JsonResponse({"success": True})
    except Credential.DoesNotExist:
        return JsonResponse({"success": False, "error": "Credential not found."}, status=404)
    

@login_required
def delete_subject_level(request, subject_level_id):
    if request.method == "POST":
        try:
            subject_level = SubjectLevel.objects.get(id=subject_level_id, tutor=request.user)
            subject_level.delete()
            return JsonResponse({"success": True, "message": "Subject deleted successfully."})
        except SubjectLevel.DoesNotExist:
            return JsonResponse({"success": False, "error": "Subject not found."})
    return JsonResponse({"success": False, "error": "Invalid request method."})


@login_required
def messages(request):
    # Fetch all unread messages for the logged-in user
    unread_messages = Message.objects.filter(receiver=request.user, read=False).order_by('-timestamp')

    return render(request, 'tutorhub/messages.html', {
        'unread_messages': unread_messages
    })


@login_required
def unread_messages_count(request):
    unread_count = Message.objects.filter(receiver=request.user, read=False).count()
    return JsonResponse({"unread_count": unread_count})


@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)

    if request.method == "POST":
        data = json.loads(request.body)
        action = data.get("action")

        if action == "edit":
            new_content = data.get("content", "").strip()
            if new_content:
                message.content = new_content
                message.edited = True
                message.edited_timestamp = now()
                message.save()
                return JsonResponse({"status": "success", "content": new_content, "edited": True})
        elif action == "delete":
            message.content = "deleted message"
            message.deleted = True
            message.save()
            return JsonResponse({"status": "success", "content": "deleted message", "deleted": True})

    return JsonResponse({"status": "error", "message": "Invalid request"})


# ****************************
# ***** Helper Functions *****
# ****************************


@login_required
def follow_tutor(request, tutor_id):
    tutor = get_object_or_404(User, id=tutor_id, is_tutor=True)
    if tutor in request.user.followed_tutors.all():
        request.user.followed_tutors.remove(tutor)
        action = "unfollowed"
    else:
        request.user.followed_tutors.add(tutor)
        action = "followed"
    return JsonResponse({"action": action, "tutor_id": tutor.id})


@login_required
def followed_tutors(request):
    followed = request.user.followed_tutors.all()
    return render(request, 'tutorhub/followed_tutors.html', {'followed': followed})


# Helper functions
def get_possessive_name(name):
    if not name:
        return "User's"
    return f"{name}'s" if not name.endswith('s') else f"{name}'"


def paginate_queryset(queryset, page_number, per_page=10):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(page_number)


# @login_required
# def create_thread(request):
#     # Extract data from the POST request
#     participants = request.POST.getlist("participants")
#     admin_user_id = request.POST.get("admin")
#     name = request.POST.get("name", "Unnamed Thread").strip()

#     # Error handling
#     if not participants:
#         return JsonResponse({"error": "Participants are required."}, status=400)
#     if not admin_user_id:
#         return JsonResponse({"error": "Admin user ID is required."}, status=400)
#     if admin_user_id not in participants:
#         return JsonResponse({"error": "Admin must be one of the participants."}, status=400)

#     # Determine if the thread is a group
#     is_group = len(participants) > 2

#     # Create the thread
#     thread = Thread.objects.create(name=name, is_group=is_group)

#     # Add participants with roles
#     for user_id in participants:
#         role = "ADMIN" if str(user_id) == admin_user_id else "MEMBER"
#         ThreadParticipant.objects.create(thread=thread, user_id=user_id, role=role)

#     # Redirect to thread detail view
#     return redirect("thread_detail", thread_id=thread.id)


# @login_required
# def remove_participant(request, thread_id, user_id):
#     try:
#         thread = Thread.objects.get(id=thread_id)
#     except Thread.DoesNotExist:
#         return JsonResponse({"error": "Thread not found."}, status=404)

#     current_user_role = ThreadParticipant.objects.filter(thread=thread, user=request.user).first()

#     if not current_user_role or current_user_role.role != "ADMIN":
#         return JsonResponse({"error": "Permission denied."}, status=403)

#     try:
#         participant = ThreadParticipant.objects.get(thread=thread, user_id=user_id)
#         participant.delete()
#         return JsonResponse({"status": "success"})
#     except ThreadParticipant.DoesNotExist:
#         return JsonResponse({"error": "Participant not found."}, status=404)


# @login_required
# def thread_detail(request, thread_id):
#     thread = get_object_or_404(Thread, id=thread_id)
#     messages = thread.messages.order_by("timestamp")

#     paginator = Paginator(messages, 20)  # 20 messages per page
#     page_obj = paginator.get_page(request.GET.get('page'))
#     return render(request, "thread_detail.html", {"thread": thread, "messages": page_obj})


# @login_required
# def send_message(request, thread_id):
#     thread = get_object_or_404(Thread, id=thread_id)
#     content = request.POST.get("content", "").strip()

#     if not content:
#         return JsonResponse({"error": "Message content cannot be empty."}, status=400)

#     Message.objects.create(thread=thread, sender=request.user, content=content)
#     return redirect("thread_detail", thread_id=thread.id)


# @login_required
# def get_thread_with_permissions(thread_id, user):
#     thread = get_object_or_404(Thread, id=thread_id)
#     participant_role = ThreadParticipant.objects.filter(thread=thread, user=user).first()
#     return thread, participant_role
