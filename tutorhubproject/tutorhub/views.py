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



from django.db.models import Q

def index(request):
    query = request.GET.get('q', '').strip()
    tutors = User.objects.filter(is_tutor=True)

    if query:
        tutors = tutors.filter(
            Q(city__icontains=query) |
            Q(state__icontains=query) |
            Q(nickname__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(tutor_subject_grades__grade_levels__icontains=query)
        ).distinct()

    paginator = Paginator(tutors, 10)  # Show 10 tutors per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'tutorhub/index.html', {'page_obj': page_obj})



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
            user.availability = request.POST.get("availability", "{}")
            user.save()

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
    # Use the logged-in user if no user_id is provided
    profile_user = request.user if user_id is None else get_object_or_404(User, id=user_id)
    credentials = profile_user.credentials.all()

    # Add an `is_image` property to each credential
    for credential in credentials:
        credential.is_image = credential.file.url.lower().endswith(('.jpg', '.jpeg', '.png'))

    return render(request, 'tutorhub/profile.html', {
        'profile': profile_user,
        'credentials': credentials,
        'is_own_profile': profile_user == request.user,
    })


@login_required
def edit_profile(request):
    profile = request.user
    if request.method == "POST":
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']
        if 'nickname' in request.POST:
            profile.nickname = request.POST.get('nickname', profile.nickname)
        if 'bio' in request.POST:
            profile.bio = request.POST.get('bio', profile.bio)
        if 'city' in request.POST:
            profile.city = request.POST.get('city', profile.city)
        if 'state' in request.POST:
            profile.state = request.POST.get('state', profile.state)
        # Handle other fields as needed
        profile.save()
        return redirect("my_profile")
    return HttpResponse(status=400)


# @login_required
# def edit_profile(request):
#     if request.method == "POST":
#         profile = request.user
#         profile.nickname = request.POST.get("nickname", profile.nickname)
#         profile.bio = request.POST.get("bio", profile.bio)
#         profile.street_address = request.POST.get("street_address", profile.street_address)
#         profile.city = request.POST.get("city", profile.city)
#         profile.state = request.POST.get("state", profile.state)
#         profile.zip_code = request.POST.get("zip_code", profile.zip_code)

#         if profile.is_tutor:
#             profile.availability = request.POST.get("availability", profile.availability)

#             # Handle subjects and grade levels
#             subject_grades = request.POST.get("subject_grades", "").split(", ")
#             profile.subject_grades.clear()
#             for item in subject_grades:
#                 subject, grade_level = item.split(" - ")
#                 sg, _ = SubjectGrade.objects.get_or_create(subject=subject, grade_level=grade_level)
#                 profile.subject_grades.add(sg)

#         profile.save()
#         return redirect("my_profile")

#     return render(request, 'tutorhub/edit_profile.html', {'profile': request.user})


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
