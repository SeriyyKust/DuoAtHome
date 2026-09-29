from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import RegistrationForm


def register(request):
    if request.user.is_authenticated:
        return redirect('account:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            account = form.save()
            login(request, account)
            return redirect('account:home')
    else:
        form = RegistrationForm()

    return render(request, 'account/register.html', {'form': form})


class AccountLoginView(LoginView):
    template_name = 'account/login.html'
    redirect_authenticated_user = True


class AccountLogoutView(LogoutView):
    """Выход из аккаунта, редирект настраивается в LOGOUT_REDIRECT_URL."""


@login_required
def home(request):
    """Главная страница пользователя (пока пустая, будет статистика)."""
    return render(request, 'account/home.html')
