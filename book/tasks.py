# -*- coding: utf-8 -*-
import datetime
import json

from google.appengine.api import urlfetch
from google.appengine.api.taskqueue import taskqueue

from book.models import Book, Ranking
from pytz import UTC

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from bs4 import BeautifulSoup


class CheckRankingPeriodicTask(APIView):
    def scrape_books(self, htmltext):
        books = []
        soup = BeautifulSoup(htmltext, "html.parser")
        for el in soup.findAll("div", {"class": "zg_itemRow"}):
            book = Book()
            book.title = el.findAll("div", {"class": "zg_title"})[0].findAll("a")[0].text.strip()
            book.url = el.findAll("div", {"class": "zg_title"})[0].findAll("a")[0].get("href").strip()
            book.id = book.url.split("/")[-1]
            book.author = el.findAll("div", {"class": "zg_byline"})[0].text.strip()
            try:
                book.price = el.findAll(
                    "span", {"class": "price"}
                )[0].findAll("b")[0].text.strip().replace(u"￥ ", "").replace(",", "")
            except:
                book.price = 0
            try:
                book.star = el.findAll(
                    "span", {"class": "a-icon-alt"}
                )[0].text.strip().replace(u"5つ星のうち ", "")
            except:
                book.star = 0
            book.image_url = el.findAll("img")[0].get("src").strip()
            books.append(book)
        return books

    def get(self, request):
        """
        定期的にAmazonのランキングを見に行くタスク
        ---
        """
        wish_list_ranking = "https://www.amazon.co.jp/gp/most-wished-for/books/"
        books = []
        # 全部のランキングを取得する
        for i in range(1, 6):
            results = urlfetch.fetch(
                url=wish_list_ranking + u"?pg=" + str(i),
                method=urlfetch.GET
            )
            books += self.scrape_books(results.content)

        # 本の情報を保存する
        today = datetime.datetime.now(UTC).date()
        for i, book in enumerate(books):
            book, is_created = Book.objects.update_or_create(
                id=book.id,
                defaults={
                    "title": book.title,
                    "url": book.url,
                    "author": book.author,
                    "price": book.price,
                    "star": book.star,
                    "image_url": book.image_url
                }
            )
            Ranking.objects.get_or_create(
                book=book,
                date=today,
                defaults={
                    "wish_ranking": i + 1
                }
            )

        taskqueue.add(
            url="/book/tasks/bookPost",
            countdown=10
        )
        return Response()



class BookPostTaskView(APIView):
    def post(self, request):
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



def post_to_slack(ranking,
                  icon=":fire:",
                  username=settings.SLACK_DEFAULTS_USERNAME,
                  channel=settings.SLACK_DEFAULTS_CHANNEL,
                  url=settings.SLACK_HOOK_URL):
    book = ranking.book
    payload = {
        "channel": channel,
        "icon_emoji": icon,
        "username": username,
        "attachments": [{
            "fallback": str(ranking.wish_ranking) + u"位: " + book.title,
            "title": str(ranking.wish_ranking) + u"位: " + book.title,
            "title_link": book.url + "?tag=kasajei-22",
            "text": book.author,
            "image_url": book.image_url,
            "color": "#eb8c11"
        }]
    }
    try:
        urlfetch.fetch(
            url=url,
            payload=json.dumps(payload),
            method=urlfetch.POST
        )
    except:
        pass

