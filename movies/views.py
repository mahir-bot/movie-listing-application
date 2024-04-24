from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Movie, Cast
from django.db.models import Q


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        new_user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=make_password(password)
        )

        new_user.save()

        return HttpResponseRedirect(reverse("signin"))

    return render(request, "movies\signup.html")


def signin_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):  
                login(request, user)  
                return redirect(reverse("home"))  
            else:
                error_message = "Invalid email or password."  
        except User.DoesNotExist:
            error_message = "Invalid email or password."  

        return render(request, "movies/signin.html", {"error_message": error_message})

    return render(request, "movies/signin.html")


def home_view(request):
    return render(request, "movies\home.html")


def search_movies(request):
    query = request.GET.get("q")

    if query:
        matching_movies = Movie.objects.filter(
            Q(title__icontains=query) |
            Q(category__icontains=query) |
            Q(cast__name__icontains=query)
        ).distinct().order_by("title")
    else:
        matching_movies = Movie.objects.all().order_by("title")

    return render(request, "search_movies.html", {"movies": matching_movies})
