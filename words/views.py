from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from account.models import Account

from .models import AccountWord, Word


def _safe_next(request, fallback):
    """Разрешаем редирект только на путь этого же сайта."""
    next_url = request.POST.get('next') or ''
    if next_url.startswith('/') and not next_url.startswith('//'):
        return next_url
    return fallback


@login_required
def words_list(request):
    """Список слов с фильтрами: направление перевода, часть речи, автор, статус."""
    direction = request.GET.get('direction', 'en-ru')
    pos = request.GET.get('pos', '')
    author = request.GET.get('author', '')
    status = request.GET.get('status', '')

    words = (
        Word.objects
        .select_related('author')
        .prefetch_related('translations')
        .order_by('title')
    )

    # ENG->RU показывает русские слова (переводим их на английский), RU->ENG — английские
    if direction == 'ru-en':
        words = words.filter(language=Word.Language.ENGLISH)
    else:
        direction = 'en-ru'
        words = words.filter(language=Word.Language.RUSSIAN)

    if pos:
        words = words.filter(part_of_speech=pos)

    if author == 'system':
        words = words.filter(author__isnull=True)
    elif author.isdigit():
        words = words.filter(author_id=int(author))

    user_statuses = {
        aw.word_id: aw.status
        for aw in AccountWord.objects.filter(account=request.user)
    }
    if status == 'none':
        words = words.exclude(pk__in=user_statuses.keys())
    elif status in AccountWord.Status.values:
        words = words.filter(pk__in=[k for k, v in user_statuses.items() if v == status])

    words = list(words)
    for word in words:
        word.user_status = user_statuses.get(word.pk)

    authors = (
        Account.objects
        .filter(words__isnull=False)
        .distinct()
        .order_by('username')
    )

    context = {
        'words': words,
        'user_statuses': user_statuses,
        'pos_choices': Word.PartOfSpeech.choices,
        'status_choices': AccountWord.Status.choices,
        'authors': authors,
        'current': {'direction': direction, 'pos': pos, 'author': author, 'status': status},
    }
    return render(request, 'words/list.html', context)


@login_required
def learn(request, word_id):
    """Кнопка «Изучать»: создаёт AccountWord или переключает статус по циклу
    нет записи → В процессе изучения → Изучено → В процессе изучения."""
    if request.method == 'POST':
        word = get_object_or_404(Word, pk=word_id)
        account_word, created = AccountWord.objects.get_or_create(
            account=request.user,
            word=word,
            defaults={'status': AccountWord.Status.IN_PROGRESS},
        )
        if not created:
            # Цикл статусов: В процессе изучения → Изучено → В процессе изучения
            if account_word.status == AccountWord.Status.IN_PROGRESS:
                account_word.status = AccountWord.Status.LEARNED
            else:
                account_word.status = AccountWord.Status.IN_PROGRESS
            account_word.save(update_fields=('status', 'updated_at'))
        return HttpResponseRedirect(_safe_next(request, reverse('words:list')))
    return redirect('words:list')
