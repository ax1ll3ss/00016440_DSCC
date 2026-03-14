from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UserRegisterForm, ProfileUpdateForm, UserLoginForm


def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your anonymous identity has been created. 👻")
            return redirect("home")
    else:
        form = UserRegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_view(request):
    """Display and update user profile."""
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, "accounts/profile.html", {"form": form})
