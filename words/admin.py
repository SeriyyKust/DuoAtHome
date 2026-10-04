from django.contrib import admin

from .models import AccountWord, Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'part_of_speech', 'author', 'created_at', 'updated_at')
    list_filter = ('language', 'part_of_speech')
    search_fields = ('title',)
    filter_horizontal = ('translations',)
    fields = ('title', 'language', 'author', 'part_of_speech', 'translations')


@admin.register(AccountWord)
class AccountWordAdmin(admin.ModelAdmin):
    list_display = ('account', 'word', 'status', 'count_error', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('account__username', 'word__title')
