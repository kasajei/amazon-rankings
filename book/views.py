# -*- coding: utf-8 -*-
import datetime

from book.models import Ranking, Book, Report
from book.serializers import BookSerializer, RankingSerializer
from book.tasks import post_to_slack
from pytz import UTC

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView


class BookView(APIView):
    def get(self, request):
        return Response()

class BookRankingView(APIView):
    def get(self, request, book_id):
        """
        本の情報をゲットする
        ---
        parameters:
                -   name: book_id
                    type: string
                    paramType: path

        """
        # book_id = request.GET.get("book_id")
        book = Book.objects.get(id=book_id)
        rankings = Ranking.objects.filter(
            book_id=book_id
        ).prefetch_related("book").order_by("-date")
        results = {
            "book": BookSerializer(book).data,
            "rankings": RankingSerializer(rankings, many=True).data
        }
        return Response(results)