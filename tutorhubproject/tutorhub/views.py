from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import User, Message, SubjectGrade, Credential
from django.db.models import Q


def index(request):
    tutors = User.objects.filter(is_tutor=True)
    return render(request, 'tutorhub/index.html', {'tutors': tutors})


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

        # Create a new user
        try:
            user = User.objects.create_user(email, email, password)
            user.nickname = request.POST.get("nickname", "")
            user.street_address = request.POST.get("street_address", "")
            user.city = request.POST.get("city", "")
            user.state = request.POST.get("state", "")
            user.zip_code = request.POST.get("zip_code", "")
            user.bio = request.POST.get("bio", "")
            user.is_tutor = (user_type == "tutor")
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "tutorhub/register.html", {
                "message": "Email address already taken."
            })

        # Handle tutor-specific fields
        if user.is_tutor:
            user.availability = request.POST.get("availability", "{}")
            user.save()

            # Process subjects and grade levels
            subjects = request.POST.getlist("subjects[]")
            for i, subject in enumerate(subjects):
                grade_levels = request.POST.getlist(f"grade_levels_{i}[]")
                SubjectGrade.objects.create(
                    tutor=user,
                    subject=subject,
                    grade_levels=grade_levels
                )


            # Process credentials
            credentials = request.FILES.getlist("credentials[]")
            for file in credentials[:7]:  # Max 7 files
                Credential.objects.create(user=user, file=file)

        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    subject_grades = SubjectGrade.objects.all()
    return render(request, "tutorhub/register.html", {
        "subject_grades": subject_grades,
    })


@login_required
def profile(request, user_id=None):
    if user_id is None:
        user_id = request.user.id

    profile_user = get_object_or_404(User, id=user_id)
    tutor_profile = getattr(profile_user, 'tutor_profile', None)

    return render(request, 'tutorhub/profile.html', {
        'profile': profile_user,
        'tutor_profile': tutor_profile,
        'subject_grades': tutor_profile.subject_grades.all() if tutor_profile else None,
        'is_own_profile': profile_user == request.user,
    })



@login_required
def my_profile(request):
    profile_user = request.user
    tutor_profile = getattr(profile_user, 'tutor_profile', None)

    return render(request, 'tutorhub/profile.html', {
        'profile': profile_user,
        'tutor_profile': tutor_profile,
        'is_own_profile': True,
    })


@login_required
def edit_profile(request):
    if request.method == "POST":
        profile = request.user
        profile.nickname = request.POST.get("nickname", profile.nickname)
        profile.bio = request.POST.get("bio", profile.bio)
        profile.street_address = request.POST.get("street_address", profile.street_address)
        profile.city = request.POST.get("city", profile.city)
        profile.state = request.POST.get("state", profile.state)
        profile.zip_code = request.POST.get("zip_code", profile.zip_code)
        profile.save()
        return redirect("my_profile")

@login_required
def edit_tutor_details(request):
    if request.method == "POST" and request.user.is_tutor:
        tutor = request.user
        tutor.availability = request.POST.get("availability", tutor.availability)
        # Handle subjects and grade levels dynamically
        subject_grades = request.POST.get("subject_grades", "").split(", ")
        tutor.subject_grades.clear()
        for item in subject_grades:
            subject, grade_level = item.split(" - ")
            sg, _ = SubjectGrade.objects.get_or_create(subject=subject, grade_level=grade_level)
            tutor.subject_grades.add(sg)
        tutor.save()
        return redirect("my_profile")


@login_required
def search_tutors(request):
    query = request.GET.get('q', '')
    results = Tutor.objects.filter(
        Q(user__nickname__icontains=query) |
        Q(subject_grades__subject__icontains=query) |
        Q(subject_grades__grade_level__icontains=query) |
        Q(user__city__icontains=query)
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
