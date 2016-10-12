from book import models
from django.contrib import admin

# Register your models here.

class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "star", "price")
    pass
admin.site.register(models.Book, BookAdmin)

class RankingAdmin(admin.ModelAdmin):
    list_display = ("date", "wish_ranking", "book")
    ordering = ("-date","wish_ranking")
admin.site.register(models.Ranking, RankingAdmin)