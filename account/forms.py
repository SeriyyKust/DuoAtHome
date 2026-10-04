from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

Account = get_user_model()


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='Имя', required=False)
    last_name = forms.CharField(label='Фамилия', required=False)
    email = forms.EmailField(label='Email', required=False)
    birthday = forms.DateField(
        label='Дата рождения',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = Account
        fields = ('username', 'first_name', 'last_name', 'email', 'birthday')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Никнейм'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повторите пароль'
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')


class AccountEditForm(forms.ModelForm):
    """Редактирование профиля на странице аккаунта."""

    class Meta:
        model = Account
        fields = ('photo', 'username', 'first_name', 'last_name', 'birthday')
        labels = {
            'photo': 'Фото',
            'username': 'Никнейм',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'birthday': 'Дата рождения',
        }
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')
