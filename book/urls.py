# -*- coding: utf-8 -*-
from book.tasks import CheckRankingPeriodicTask, BookPostTaskView, PostToTitter
from book.views import BookView, BookRankingView
from django.conf.urls import url


urlpatterns = [
    url(r'^$', BookView.as_view()),
    # url(r'^(?P<book_id>.+)$', BookRankingView.as_view()),
    url(r'^tasks/bookPost', BookPostTaskView.as_view()),
    url(r'^tasks/tweet', PostToTitter.as_view()),
    url(r'^tasks/periodic/checkRanking', CheckRankingPeriodicTask.as_view()),
]
