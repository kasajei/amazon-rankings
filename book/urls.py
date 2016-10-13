# -*- coding: utf-8 -*-
from book.tasks import CheckRankingPeriodicTask, BookPostTaskView
from book.views import BookView
from django.conf.urls import url


urlpatterns = [
    url(r'^$', BookView.as_view()),
    url(r'^tasks/bookPost', BookPostTaskView.as_view()),
    url(r'^tasks/periodic/checkRanking', CheckRankingPeriodicTask.as_view()),
]
