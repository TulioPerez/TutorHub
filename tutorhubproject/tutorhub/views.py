from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import User, Tutor, Message, Subject, GradeLevel, User, Credential
from django.db.models import Q


def index(request):
    if request.user.is_authenticated:
        return redirect('search_tutors')
    return render(request, 'tutorhub/index.html')


# authentication
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

        # Attempt to create new user
        try:
            user = User.objects.create_user(email, email, password)
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "tutorhub/register.html", {
                "message": "Email address already taken."
            })
        
          # Handle tutor-specific fields
        if user_type == "tutor":
            tutor = Tutor.objects.create(user=user)

            tutor.availability = request.POST.get("availability", "{}")
            tutor.save()

            # Add subjects and grade levels
            subjects = request.POST.getlist("subjects")
            grade_levels = request.POST.getlist("grade_levels")
            tutor.subjects.add(*Subject.objects.filter(id__in=subjects))
            tutor.grade_levels.add(*GradeLevel.objects.filter(id__in=grade_levels))
        
            # Process credential uploads
            credentials = request.FILES.getlist("credentials")
            for file in credentials[:5]:  # Enforce max 5 files
                Credential.objects.create(tutor=tutor, file=file)

        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    # Pass subject and grade-level data for the form
    subjects = Subject.objects.all()
    grade_levels = GradeLevel.objects.all()
    return render(request, "tutorhub/register.html", {
        "subjects": subjects,
        "grade_levels": grade_levels
    })


@login_required
def profile(request, user_id=None):
    if user_id is None:
        user_id = request.user.id

    profile_user = get_object_or_404(User, id=user_id)
    is_own_profile = profile_user == request.user

    if request.method == "POST" and is_own_profile:
        profile_user.nickname = request.POST.get("nickname", profile_user.nickname)
        profile_user.bio = request.POST.get("bio", profile_user.bio)
        profile_user.address = request.POST.get("address", profile_user.address)
        profile_user.save()
        return redirect("profile", user_id=profile_user.id)

    return render(request, 'tutorhub/profile.html', {
        'profile': profile_user,
        'is_own_profile': is_own_profile,
    })


@login_required
def search_tutors(request):
    query = request.GET.get('q', '')
    results = Tutor.objects.filter(
        Q(user__nickname__icontains=query) |
        Q(subjects__name__icontains=query) |
        Q(user__address__icontains=query)
    ).distinct()
    return render(request, 'tutorhub/tutors.html', {'results': results})


@login_required
def like_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, id=tutor_id)
    if tutor in request.user.liked_tutors.all():
        request.user.liked_tutors.remove(tutor)
    else:
        request.user.liked_tutors.add(tutor)
    return redirect('liked_tutors')


@login_required
def liked_tutors(request):
    liked = request.user.liked_tutors.all()
    return render(request, 'tutorhub/liked_tutors.html', {'liked': liked})


@login_required
def message_list(request):
    messages = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by('-timestamp')
    return render(request, 'tutorhub/messages.html', {'messages': messages})


@login_required
def send_message(request, receiver_id):
    receiver = get_object_or_404(User, id=receiver_id)
    if request.method == "POST":
        content = request.POST['content']
        Message.objects.create(sender=request.user, receiver=receiver, content=content)
        return redirect('message_list')
    return render(request, 'tutorhub/send_message.html', {'receiver': receiver})
