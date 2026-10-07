from django.conf import settings
from django.db import models


class Word(models.Model):
    """Слово с переводами на другой язык."""

    class Language(models.TextChoices):
        ENGLISH = 'en', 'English'
        RUSSIAN = 'ru', 'Russian'

    class PartOfSpeech(models.TextChoices):
        NOUN = 'noun', 'существительное'
        VERB = 'verb', 'глагол'
        ADJECTIVE = 'adjective', 'прилагательное'
        ADVERB = 'adverb', 'наречие'
        PRONOUN = 'pronoun', 'местоимение'
        PREPOSITION = 'preposition', 'предлог'
        CONJUNCTION = 'conjunction', 'союз'
        NUMERAL = 'numeral', 'числительное'
        INTERJECTION = 'interjection', 'междометие'

    title = models.CharField('Слово', max_length=64, unique=True)
    language = models.CharField('Язык', max_length=2, choices=Language.choices)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='words',
    )
    part_of_speech = models.CharField('Часть речи', max_length=16, choices=PartOfSpeech.choices)
    translations = models.ManyToManyField('self', verbose_name='Переводы', symmetrical=True, blank=True)
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Время обновления', auto_now=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return f'{self.title} ({self.get_language_display()}, {self.get_part_of_speech_display()})'


class AccountWord(models.Model):
    """Связь аккаунта со словом: знает ли пользователь слово и как хорошо."""

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'В процессе изучения'
        LEARNED = 'learned', 'Изучено'

    account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Аккаунт',
        on_delete=models.CASCADE,
        related_name='account_words',
    )
    word = models.ForeignKey(
        Word,
        verbose_name='Слово',
        on_delete=models.CASCADE,
        related_name='account_words',
    )
    status = models.CharField('Статус', max_length=16, choices=Status.choices)
    count_error = models.IntegerField('Количество ошибок', default=0)
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Время обновления', auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('account', 'word'), name='unique_account_word'),
        ]

    def __str__(self):
        return f'{self.account} — {self.word} ({self.get_status_display()})'
