from django import forms
from django.contrib import admin

from .models import AccountWord, Word


class WordAdminForm(forms.ModelForm):
    """Форма слова с валидацией переводов: другой язык, та же часть речи.

    Дублирует проверки сигнала m2m_changed, но ошибки показываются
    в форме админки, а не падают серверной ошибкой при save_m2m().
    """

    class Meta:
        model = Word
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        translations = cleaned.get('translations')
        language = cleaned.get('language')
        pos = cleaned.get('part_of_speech')
        if not translations:
            return cleaned
        for word in translations:
            if language and word.language == language:
                self.add_error('translations', (
                    f'«{word.title}» — тот же язык ({word.get_language_display()}); '
                    f'перевод должен быть на другом языке.'
                ))
            elif pos and word.part_of_speech != pos:
                self.add_error('translations', (
                    f'«{word.title}»: часть речи ({word.get_part_of_speech_display()}) '
                    f'не совпадает с частью речи слова.'
                ))
        return cleaned


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    form = WordAdminForm
    list_display = ('title', 'language', 'part_of_speech', 'author', 'translations_count', 'created_at', 'updated_at')
    list_filter = ('language', 'part_of_speech', 'author')
    search_fields = ('title',)
    filter_horizontal = ('translations',)
    fields = ('title', 'language', 'part_of_speech', 'author', 'translations')

    @admin.display(description='Переводов')
    def translations_count(self, obj):
        return obj.translations.count()


@admin.register(AccountWord)
class AccountWordAdmin(admin.ModelAdmin):
    list_display = ('account', 'word', 'status', 'count_error', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('account__username', 'word__title')
