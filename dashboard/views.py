from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from movies.models import FavoriteMovies
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Create your views here.


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
        "account/user_profile.html",
        {
            'user': user,
            'favorite_movies': favorite_movies,
        }
    )


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })
