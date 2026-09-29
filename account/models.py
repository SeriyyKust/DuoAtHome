from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):
    """Пользовательская модель аккаунта, расширяет базового User."""

    birthday = models.DateField('Дата рождения', null=True, blank=True)
    photo = models.ImageField('Фото', upload_to='account/photos/', null=True, blank=True)

    # В дальнейшем здесь будут добавляться новые поля
