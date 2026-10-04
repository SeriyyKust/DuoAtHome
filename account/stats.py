"""Заглушки данных для статистики на главной странице.

Пока все показатели выдуманы. В дальнейшем здесь появится
вычисление реальных значений из базы данных.
"""
import random
from datetime import date, timedelta

# Последние выученные слова: слово, перевод, сколько дней назад выучено
RECENT_WORDS = [
    {'word': 'reluctant', 'translation': 'нерешительный', 'days_ago': 1},
    {'word': 'abundant', 'translation': 'изобильный', 'days_ago': 1},
    {'word': 'improve', 'translation': 'улучшать', 'days_ago': 2},
    {'word': 'achieve', 'translation': 'достигать', 'days_ago': 3},
    {'word': 'borrow', 'translation': 'занимать (брать взаймы)', 'days_ago': 4},
    {'word': 'weather', 'translation': 'погода', 'days_ago': 5},
    {'word': 'journey', 'translation': 'путешествие', 'days_ago': 6},
    {'word': 'knowledge', 'translation': 'знание', 'days_ago': 8},
    {'word': 'curious', 'translation': 'любопытный', 'days_ago': 11},
    {'word': 'brave', 'translation': 'храбрый', 'days_ago': 14},
]

# Слова с наибольшим количеством ошибок в переводе
PROBLEM_WORDS = [
    {'word': 'receive', 'translation': 'получать', 'mistakes': 14},
    {'word': 'stationery', 'translation': 'канцелярские товары', 'mistakes': 12},
    {'word': 'affect', 'translation': 'влиять', 'mistakes': 11},
    {'word': 'effect', 'translation': 'эффект', 'mistakes': 10},
    {'word': 'principal', 'translation': 'основной', 'mistakes': 9},
    {'word': 'principle', 'translation': 'принцип', 'mistakes': 8},
    {'word': 'desert', 'translation': 'пустыня', 'mistakes': 7},
    {'word': 'dessert', 'translation': 'десерт', 'mistakes': 6},
    {'word': 'quite', 'translation': 'довольно', 'mistakes': 5},
    {'word': 'quiet', 'translation': 'тихий', 'mistakes': 5},
]


def get_activity_data(user):
    """Ежедневная активность за последний год: [{'date', 'count'}, ...]."""
    rng = random.Random(f'activity:{user.pk}:{user.username}')
    today = date.today()
    days = []
    for i in range(364, -1, -1):
        day = today - timedelta(days=i)
        # Имитация: часть дней без активности, часть с умеренной, часть с высокой
        count = rng.choice([
            0, 0,
            rng.randint(0, 9),
            rng.randint(5, 18),
            rng.randint(12, 34),
            rng.randint(28, 45),
        ])
        days.append({'date': day.isoformat(), 'count': count})
    return {'days': days}


def get_words_stats(user):
    """Сводка по словам: выучено / на повторении / к изучению + таблицы."""
    return {
        'learned': 128,
        'review': 42,
        'to_learn': 65,
        'recent': RECENT_WORDS,
        'problem': PROBLEM_WORDS,
    }
