from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


def _resolve_username(value: str) -> str:
    """Allow login by username or by email address."""
    if "@" not in value:
        return value

    try:
        return User.objects.get(email__iexact=value).username
    except User.DoesNotExist:
        return value


def _find_user(identifier: str):
    user = User.objects.filter(username__iexact=identifier).first()

    if user is None and "@" in identifier:
        user = User.objects.filter(email__iexact=identifier).first()

    return user


def index(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not identifier:
            messages.error(request, "Vul een gebruikersnaam of e-mailadres in.")
            return render(request, "login/login.html")

        user = _find_user(identifier)

        if user is None:
            messages.error(request, "Onjuiste gebruikersnaam of e-mailadres.")
            return render(request, "login/login.html")

        if not user.is_active:
            messages.error(request, "Dit account is uitgeschakeld.")
            return render(request, "login/login.html")

        if password == "":
            if not user.has_usable_password():
                auth_login(request, user)
                return redirect("/")

            messages.error(request, "Wachtwoord is verplicht voor dit account.")
            return render(request, "login/login.html")

        username = _resolve_username(identifier)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("/")

        messages.error(request, "Onjuiste e-mail/gebruikersnaam of wachtwoord.")

    return render(request, "login/login.html")


def logout_view(request):
    if request.method == "POST":
        auth_logout(request)
        return redirect("/login/")

    return redirect("/")
