# -*- coding: utf-8 -*-
from book.tasks import CheckRankingPeriodicTask
from django.conf.urls import url


urlpatterns = [
    url(r'^tasks/periodic/checkRanking', CheckRankingPeriodicTask.as_view()),
]
