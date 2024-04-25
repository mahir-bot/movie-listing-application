from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import AddCastForm, AddCategoryForm, MovieForm
from .models import Cast, Category, FavoriteMovies, Movie, User


def user_register(request):
    """
    Register a new user.

    This function handles the registration of a new user. It checks if the user is already authenticated and if so, redirects them to the home page. If the user is not authenticated, it checks if the request method is POST. If it is, it creates a new user using the provided username, first name, last name, email, and password from the request POST data. It then displays a success message and redirects the user to the sign-in page. If an exception occurs during the user creation process, it prints the exception and renders the sign-up page.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: If the user is already authenticated, redirects them to the home page.
        HttpResponse: If the user is not authenticated and the request method is POST, redirects the user to the sign-in page after creating a new user. If an exception occurs, renders the sign-up page.

    """
    if request.user.is_authenticated:
        return redirect('home')
    else:
        try:
            if request.method == 'POST':
                User.objects.create_user(
                    username=request.POST['username'],
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name'],
                    email=request.POST["email"],
                    password=request.POST["password"]
                )
                messages.success(request, 'Account created successfully')
                return redirect('signin')
        except Exception as e:
            print(e)
        return render(request, 'movies/signup.html')


def user_login(request):
    """
    Logs in a user.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: If the user is already authenticated, redirects them to the home page.
        HttpResponse: If the user is not authenticated and the request method is POST, redirects the user to the home page after successful login.
                      If the user credentials are invalid, displays an error message.
                      Otherwise, renders the signin.html template.
    """
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            user = authenticate(
                email=request.POST["email"],
                password=request.POST['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials')

        return render(request, 'movies/signin.html', {})


@login_required(login_url='login')
def user_logout(request):
    """
    Logs out a user if authenticated and redirects to the home page.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: If the user is authenticated and successfully logs out, redirects them to the home page.
    """
    if request.user.is_authenticated:
        logout(request)
        return redirect('home')


@login_required
def user_profile(request):
    """
    A view function to display a user's profile page with their favorite movies.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the user's profile page with user data and favorite movies.
    """
    user = request.user
    favorite_movies = FavoriteMovies.objects.filter(
        user=user)
    print(favorite_movies)
    return render(
        request,
        "movies/user_profile.html",
        {
            'user': user,
            'favorite_movies': favorite_movies,
        }
    )


def home_page(request):
    """
    Renders the home page with a paginated list of movies.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the home.html template with a paginated list of movies.
    """
    movies = Movie.objects.all().order_by("title")
    paginator = Paginator(movies, 30)
    page_number = request.GET.get('page', 1)
    page_movies = paginator.get_page(page_number)
    return render(request, "movies/home.html", {"movies": page_movies})


def search_movies(request):
    """
    A function to search movies based on a query parameter in the request.

    Parameters:
        request (HttpRequest): The HTTP request object containing the query parameter.

    Returns:
        HttpResponse: Renders the search_movies.html template with matching movies based on the query.
    """
    query = request.GET.get("q")

    if query:
        matching_movies = Movie.objects.filter(
            Q(title__icontains=query) |
            Q(category__name__icontains=query) |
            Q(casts__name__icontains=query)
        ).distinct().order_by("title")
    else:
        return redirect("home")

    return render(request, "movies/search_movies.html", {"movies": matching_movies, "query": query})


def create_movie(request):
    """
    Creates a new movie based on the provided request.

    Parameters:
        request (HttpRequest): The HTTP request object containing the movie data.

    Returns:
        HttpResponseRedirect: Redirects to the home page if the movie is successfully created.
        HttpResponse: Renders the create_movie.html template with the form if the request method is not POST or if the form is invalid.
    """

    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save(commit=False)
            movie.save()
            category_ids = request.POST.getlist("category")
            cast_ids = request.POST.getlist(
                "casts")

            if category_ids:
                movie.category.set(
                    Category.objects.filter(id__in=category_ids))
                print(category_ids)

            if cast_ids:
                movie.casts.set(Cast.objects.filter(id__in=cast_ids))
                print(cast_ids)

            print(movie)
            movie.save()

            messages.success(request, "Movie created successfully!")

            return redirect(reverse("home"))

        else:
            messages.error(
                request, "There were errors in the form. Please check your inputs.")
    else:
        form = MovieForm()
    categories = Category.objects.all()
    casts = Cast.objects.all()

    return render(
        request,
        "movies/create_movie.html",
        {
            "form": form,
            "categories": categories,
            "casts": casts,
        },
    )


def movie_details(request, movie_slug):
    """
    Retrieves details of a specific movie based on the provided movie slug.

    Parameters:
        request (HttpRequest): The HTTP request object.
        movie_slug (str): The unique slug identifier of the movie.

    Returns:
        HttpResponse: Renders the movie details page with the movie information.
    """
    movie = get_object_or_404(Movie, slug=movie_slug)
    is_favorite = False
    if request.user.is_authenticated:
        if FavoriteMovies.objects.filter(user=request.user, movie=movie).exists():
            is_favorite = True
    return render(request, 'movies/movie_detail.html', {'movie': movie, 'is_favorite': is_favorite})


def update_movie(request, movie_slug):
    """
    Updates a movie with the given slug using the provided request.

    Args:
        request (HttpRequest): The HTTP request object containing the movie data.
        movie_slug (str): The unique slug identifier of the movie to be updated.

    Returns:
        HttpResponseRedirect: Redirects to the movie detail page after successful update.
        HttpResponse: Renders the update movie form if the request method is not POST.

    Raises:
        Http404: If no movie with the given slug is found.
    """
    movie = get_object_or_404(Movie, slug=movie_slug)

    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES,
                         instance=movie)
        if form.is_valid():
            form.save()
            return redirect(reverse("movie_detail", kwargs={"movie_slug": movie.slug}))
    else:
        form = MovieForm(instance=movie)

    return render(request, "movies/update_movie.html", {"form": form})


def delete_movie(request, movie_slug):
    """
    Deletes a movie based on the provided movie slug.

    Parameters:
        request (HttpRequest): The HTTP request object containing the request data.
        movie_slug (str): The unique slug identifier of the movie to be deleted.

    Returns:
        HttpResponseRedirect: Redirects to the home page if the movie is successfully deleted.
        HttpResponse: Renders the delete confirmation page if the request method is not POST.
    """
    movie = get_object_or_404(Movie, slug=movie_slug)

    if request.method == "POST":
        movie.delete()
        return redirect(reverse("home"))

    return render(request, "movies/movie_delete.html", {"movie": movie})


@login_required
def favorite_movies(request):
    """
    A view function to display a user's favorite movies.

    This function is decorated with `@login_required`, which means that only authenticated
    users can access this view.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the "movies/search_favorites.html" template with the user's
        favorite movies. The context includes a dictionary with the key "favorite_movies"
        and the value of the user's favorite movies.
    """
    user = request.user
    favorite_movies = FavoriteMovies.objects.filter(user=user)
    return render(
        request,
        "movies/favorite_movies.html",
        {
            "favorite_movies": favorite_movies,
        },
    )


@login_required
def add_favorite_movie(request, movie_slug):
    """
    Adds a movie to the user's favorite list if the user is authenticated.

    Parameters:
        request (HttpRequest): The HTTP request object.
        movie_slug (str): The slug of the movie to be added to the favorite list.

    Returns:
        HttpResponseRedirect: Redirects to the movie detail page if the movie is successfully added to the favorite list.
        HttpResponseRedirect: Redirects to the signin page if the user is not authenticated.
        HttpResponseRedirect: Redirects to the home page if the request method is not POST or if the form is invalid.
    """
    if request.method == "POST":
        movie = get_object_or_404(Movie, slug=movie_slug)
        user = request.user
        if not FavoriteMovies.objects.filter(user=user, movie=movie).exists():
            FavoriteMovies.objects.create(user=user, movie=movie)

        return redirect(reverse("movie_detail", args=[movie_slug]))

    return redirect(reverse("home"))


@login_required
def search_favorite_movies(request):
    """
    A view function to search for favorite movies based on a query parameter in the request.

    This function is decorated with `@login_required`, which means that only authenticated
    users can access this view.

    Parameters:
        request (HttpRequest): The HTTP request object containing the query parameter.

    Returns:
        HttpResponse: Renders the "movies/favorite_movies.html" template with matching favorite movies 
                      based on the query. The context includes a dictionary with the keys "query" and 
                      "movies", where "movies" is a queryset of favorite movies matching the query.
    """
    query = request.GET.get("q", "").strip()
    user = request.user
    favorite_movies = FavoriteMovies.objects.filter(user=user)

    if query:
        favorite_movies = favorite_movies.filter(
            Q(movie__title__icontains=query) |
            Q(movie__category__name__icontains=query) |
            Q(movie__casts__name__icontains=query)
        ).distinct().order_by("movie__title")
    else:
        return redirect(reverse("favorite_movies"))
    return render(
        request,
        "movies/search_favorites.html",
        {
            "query": query,
            "movies": favorite_movies,
        },
    )


@login_required
def delete_favorite_movie(request, movie_slug):
    """
    Deletes a favorite movie for the authenticated user.

    Parameters:
        request (HttpRequest): The HTTP request object containing the request data.
        movie_slug (str): The unique slug identifier of the movie to be deleted.

    Returns:
        HttpResponseRedirect: Redirects to the movie detail page if the movie is successfully deleted.
        HttpResponseRedirect: Redirects to the signin page if the user is not authenticated.
        HttpResponseRedirect: Redirects to the home page if the request method is not POST.
    """

    if request.method == "POST":
        movie = get_object_or_404(Movie, slug=movie_slug)
        user = request.user
        FavoriteMovies.objects.filter(user=user, movie=movie).delete()
        return redirect(reverse("movie_detail", args=[movie_slug]))

    return redirect(reverse("home"))


def add_cast(request):
    """
    Adds a cast member to the database.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the "create_movie" page if the cast member is successfully added.
        HttpResponse: Renders the "movies/add_cast.html" template with the form if the request method is not POST or if the form is invalid.
    """
    if request.method == "POST":
        form = AddCastForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("create_movie"))
    else:
        form = AddCastForm()

    return render(request, "movies/add_cast.html", {"form": form})


def add_category(request):
    """
    Adds a category to the database.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the "create_movie" page if the category is successfully added.
        HttpResponse: Renders the "movies/add_category.html" template with the form if the request method is not POST or if the form is invalid.
    """
    if request.method == "POST":
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("create_movie"))
    else:
        form = AddCategoryForm()

    return render(request, "movies/add_category.html", {"form": form})
