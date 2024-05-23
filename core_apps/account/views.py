from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from .models import User
from core import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .utils import genarate_token
import threading


class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


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
                data = User.objects.create_user(
                    username=request.POST['username'],
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name'],
                    email=request.POST["email"],
                    password=request.POST["password"],
                    is_active=False
                )
                current_site = get_current_site(request)
                email_subject = 'Activate your account'

                message = render_to_string('account/activate.html', {
                    'user': request.user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(data.pk)),
                    'token': genarate_token.make_token(data)
                })

                email_message = EmailMessage(email_subject, message, settings.DEFAULT_FROM_EMAIL, to=[
                    data.email])
                EmailThread(email_message).start()
                messages.success(request, 'Account created successfully')
                return redirect('signin')
        except Exception as e:
            print(e)
    return render(request, 'account/signup.html')


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
                if user.is_active:
                    login(request, user)
                    return redirect('home')
                else:
                    messages.error(
                        request, 'Your account is not activated. Please check your email to activate your account.')
            else:
                messages.error(request, 'Invalid credentials')

        return render(request, 'account/signin.html', {})


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


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and genarate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Account activated successfully')
            return redirect('signin')
        else:
            messages.error(request, 'Invalid activation link')
            return render(request, 'account/activate_failed.html', status=401)
