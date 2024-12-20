from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import User, Message, SubjectGrade, Credential
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.http import JsonResponse
from django.utils.timezone import now
import json
from django.db.models import Q


def index(request):
    query = request.GET.get('q', '').strip()
    view_type = request.GET.get('view', 'all')
    tutors = User.objects.filter(is_tutor=True).order_by('nickname')

    if view_type == "search" and query:
        tutors = tutors.filter(
            Q(city__icontains=query) |
            Q(state__icontains=query) |
            Q(nickname__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(tutor_subject_grades__grade_levels__icontains=query)
        ).distinct()
    
    # Handle following listing
    elif view_type == "following" and request.user.is_authenticated:
        tutors = request.user.followed_tutors.all()

    # Pagination
    paginator = Paginator(tutors, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

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
            user.street_address = request.POST.get("street_address", "")
            user.city = request.POST.get("city", "")
            user.state = request.POST.get("state", "")
            user.zip_code = request.POST.get("zip_code", "")
            user.bio = request.POST.get("bio", "")
            user.is_tutor = (user_type == "tutor")

            # Handle profile image
            if 'profile_image' in request.FILES:
                user.profile_image = request.FILES['profile_image']
                user.save()

            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "tutorhub/register.html", {
                "message": "Email address already taken."
            })

        # Handle tutor-specific fields
        if user.is_tutor:

            # Process subjects and grade levels
            subjects = request.POST.getlist("subjects[]")
            for i, subject in enumerate(subjects):
                grade_levels = request.POST.getlist(f"grade_levels_{i}[]")
                if grade_levels:
                    SubjectGrade.objects.create(
                        tutor=user,
                        subject=subject,
                        grade_levels=grade_levels
                    )

            # Process credentials
            credentials = request.FILES.getlist("credentials[]")
            for file in credentials[:7]:
                if file.size > 5 * 1024 * 1024:
                    return render(request, "tutorhub/register.html", {
                        "message": "One or more files exceed the maximum allowed size of 5MB."
                    })
                Credential.objects.create(user=user, file=file)

        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    subject_grades = SubjectGrade.objects.all()
    return render(request, "tutorhub/register.html", {
        "subject_grades": subject_grades,
    })


@login_required
def profile(request, user_id=None):
    profile_user = request.user if user_id is None else get_object_or_404(User, id=user_id)
    credentials = profile_user.credentials.all()
    scroll_to = request.GET.get('scroll_to')
    grade_levels = ['PK / KG', '1 - 5', '6 - 8', '9 - 12', 'Adults']
    subject_grades = profile_user.tutor_subject_grades.all()

    messages = Message.objects.filter(
        (Q(sender=request.user, receiver=profile_user) | Q(sender=profile_user, receiver=request.user))
    ).order_by('timestamp')

    # Auto scroll to unread messages
    if scroll_to:
        try:
            message_to_mark = messages.get(id=scroll_to, receiver=request.user, read=False)
            message_to_mark.read = True
            message_to_mark.save()
        except Message.DoesNotExist:
            pass

    # Handle credentials
    for credential in credentials:
        credential.is_image = credential.file.url.lower().endswith(('.jpg', '.jpeg', '.png'))

    # Handle messaging
    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=profile_user, content=content)
        return redirect('profile', user_id=user_id)

    # List of days to pass to the template
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    return render(request, 'tutorhub/profile.html', {
        'profile': profile_user,
        'credentials': credentials,
        'grade_levels': grade_levels,
        'subject_grades': subject_grades,
        'is_own_profile': profile_user == request.user,
        'days_of_week': days_of_week,
        'messages': messages,
        'scroll_to': scroll_to
    })


@login_required
def edit_profile(request):
    profile = request.user
    
    if request.method == "POST":

        # Subjects and grades editing
        subjects = request.POST.getlist("subjects[]")
        all_grade_levels = [request.POST.getlist(f"grade_levels_{i}[]") for i in range(len(subjects))]

        profile.subject_grades.all().delete()
        for subject, grade_levels in zip(subjects, all_grade_levels):
            if subject and grade_levels:
                SubjectGrade.objects.create(tutor=profile, subject=subject, grade_levels=grade_levels)

        # Availability editing
        availability_days = request.POST.getlist("availability_days[]")
        availability_start = request.POST.getlist("availability_start[]")
        availability_end = request.POST.getlist("availability_end[]")
        
        if availability_days and availability_start and availability_end:
            profile.availability = [
                {"day": day, "start": start, "end": end}
                for day, start, end in zip(availability_days, availability_start, availability_end)
            ]

        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']
        if 'nickname' in request.POST:
            profile.nickname = request.POST.get('nickname', profile.nickname)
        if 'first_name' in request.POST:
            profile.first_name = request.POST.get('first_name', profile.first_name)
        if 'last_name' in request.POST:
            profile.last_name = request.POST.get('last_name', profile.last_name)
        if 'bio' in request.POST:
            profile.bio = request.POST.get('bio', profile.bio)
        if 'city' in request.POST:
            profile.city = request.POST.get('city', profile.city)
        if 'state' in request.POST:
            profile.state = request.POST.get('state', profile.state)
        if 'credentials[]' in request.FILES:
            for uploaded_file in request.FILES.getlist("credentials[]"):
                Credential.objects.create(user=profile, file=uploaded_file)

        # Save changes and redirect to profile page
        profile.save()
        return redirect("my_profile")
    return HttpResponse(status=400)


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


@login_required
def delete_credential(request, credential_id):
    try:
        credential = Credential.objects.get(id=credential_id, user=request.user)
        credential.delete()
        return JsonResponse({"success": True})
    except Credential.DoesNotExist:
        return JsonResponse({"success": False, "error": "Credential not found."}, status=404)


@login_required
def search_tutors(request):
    query = request.GET.get('q', '')
    results = User.objects.filter(
        Q(nickname__icontains=query) |
        Q(tutor_subject_grades__subject__icontains=query) |
        Q(city__icontains=query),
        is_tutor=True,
    ).distinct()

    return render(request, 'tutorhub/tutors.html', {'results': results})


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
