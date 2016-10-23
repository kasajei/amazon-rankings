# -*- coding: utf-8 -*-
from book.views import BookView, BookRankingView
from django.conf.urls import url

urlpatterns = [
    url(r'^$', BookView.as_view()),
    url(r'^(?P<book_id>.+)$', BookRankingView.as_view())
]
