# -*- coding: utf-8 -*-
import datetime

from book.models import Ranking, Book
from book.tasks import post_to_slack
from pytz import UTC

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView


class BookView(APIView):
    def get(self, request):
        now = datetime.datetime.now(UTC)
        one_day_ago = now - datetime.timedelta(days=1)
        today = now.date()
        yesterday = one_day_ago.date()
        yesterday_ranking = Ranking.objects.filter(date=yesterday).values_list("book_id", flat=True)
        today_ranking = Ranking.objects.filter(date=today).values_list("book_id", flat=True)
        diff = filter(lambda x: x not in yesterday_ranking, today_ranking)
        # TODO: 以前に通知したかどうか
        rankings = Ranking.objects.filter(book_id__in=diff).prefetch_related("book").order_by("-wish_ranking")
        for ranking in rankings:
            post_to_slack(ranking)
        return Response()