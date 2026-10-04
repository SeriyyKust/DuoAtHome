"""Валидация связей переводов.

Ограничения «у перевода должен быть другой язык» и «части речи должны
совпадать» связывают две строки таблицы, поэтому их нельзя выразить
CHECK-констрейнтом БД — проверяем сигналом до вставки связи.
"""
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Word


@receiver(m2m_changed, sender=Word.translations.through)
def validate_translation_links(sender, instance, action, pk_set, **kwargs):
    if action != 'pre_add':
        return

    targets = Word.objects.filter(pk__in=pk_set)
    for target in targets:
        if target.pk == instance.pk:
            raise ValidationError('Слово не может быть переводом самого себя.')
        if target.language == instance.language:
            raise ValidationError(
                f'У перевода должен быть другой язык: '
                f'«{instance.title}» ({instance.get_language_display()}) → '
                f'«{target.title}» ({target.get_language_display()}).'
            )
        if target.part_of_speech != instance.part_of_speech:
            raise ValidationError(
                f'У слов, связанных переводом, должны совпадать части речи: '
                f'«{instance.title}» ({instance.get_part_of_speech_display()}) → '
                f'«{target.title}» ({target.get_part_of_speech_display()}).'
            )
