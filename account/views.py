from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import AccountEditForm, RegistrationForm


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


@login_required
def edit(request):
    """Страница редактирования аккаунта."""
    account = request.user
    # Старое имя файла берём из БД: форма заменяет account.photo ещё на этапе валидации
    old_photo_name = (
        get_user_model().objects.filter(pk=account.pk).values_list('photo', flat=True).first()
    )

    if request.method == 'POST':
        form = AccountEditForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            form.save()
            # Удаляем старый файл фото, если он заменён или снят
            new_photo_name = account.photo.name if account.photo else None
            if old_photo_name and old_photo_name != new_photo_name:
                account.photo.storage.delete(old_photo_name)
            return redirect('account:home')
    else:
        form = AccountEditForm(instance=account)

    return render(request, 'account/edit.html', {'form': form})


@login_required
@require_POST
def delete(request):
    """Полное удаление аккаунта."""
    account = request.user
    if account.photo:
        account.photo.delete(save=False)
    account.delete()
    logout(request)
    return redirect('account:login')
