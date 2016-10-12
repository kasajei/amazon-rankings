# -*- coding: utf-8 -*-
import datetime
from google.appengine.api import urlfetch

import requests
from book.models import Book, Ranking
from pytz import UTC
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
                book.price = el.findAll("span", {"class": "price"})[0].findAll("b")[0].text.strip().replace(u"￥ ", "").replace(",", "")
            except:
                book.price = 0
            try:
                book.star = el.findAll("span", {"class": "a-icon-alt"})[0].text.strip().replace(u"5つ星のうち ", "")
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
            print wish_list_ranking + u"?pg=" + str(i)
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

        return Response()