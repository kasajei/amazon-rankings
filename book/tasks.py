# -*- coding: utf-8 -*-
import datetime
import json
import logging

import tweepy
from google.appengine.api import urlfetch
from google.appengine.api.taskqueue import taskqueue

from book.models import Book, Ranking, Report
from pytz import UTC

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from bs4 import BeautifulSoup
import bitly_api


def get_shot_url(url):
    bitly = bitly_api.Connection(settings.BITLY_LOGIN, settings.BITLY_API_KEY)
    return bitly.shorten(url)["url"].encode("utf-8")

class CheckRankingPeriodicTask(APIView):
    def scrape_books(self, htmltext):
        books = []
        soup = BeautifulSoup(htmltext, "html.parser")
        for el in soup.findAll("div", {"class": "zg_itemRow"}):
            book = Book()
            book.title = el.findAll("img")[0].get("alt", "").encode("utf-8")
            book.url = "https://www.amazon.co.jp/"+el.findAll("a", {"class": "a-link-normal"})[0].get("href").strip()
            book.id = book.url.split("/")[-1].split("?")[0]
            try :
                book.author = el.findAll("div", {"class": "a-row a-size-small"})[0].findAll("a",{"class":"a-size-small a-link-child"})[0].text.strip()
            except:
                try:
                    book.author = el.findAll("div", {"class": "a-row a-size-small"})[0].findAll("span",{"class":"a-size-small a-color-base"})[0].text.strip()
                except:
                    book.author = u"著者不明"
            try:
                book.price = int(el.findAll(
                    "span", {"class": "a-size-base a-color-price"}
                )[0].text.strip().replace(u"￥", "").replace(",", ""))
            except:
                book.price = 0
            try:
                book.star = float(el.findAll("i", {"class": "a-icon-star"})[0].findAll(
                    "span", {"class": "a-icon-alt"}
                )[0].text.strip().replace(u"5つ星のうち ", ""))
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
        today_ranking = Ranking.objects.filter(date=today).order_by("wish_ranking").values_list("book_id", flat=True)
        diff = filter(lambda x: x not in yesterday_ranking, today_ranking)
        diff = diff[:30]
        reported = Report.objects.filter(book_id__in=diff).values_list("book_id", flat=True)
        report = filter(lambda x: x not in reported, diff)
        rankings = Ranking.objects.filter(
            date=today,
            book_id__in=report
        ).prefetch_related("book").order_by("-wish_ranking")
        for ranking in rankings:
            if not settings.DEBUG:
                post_to_twitter(
                    ranking.book.author + u"「" + ranking.book.title + u"」\n\n" + get_shot_url(ranking.book.url+u"?tag=kasajei-22")
                )
                post_to_slack(ranking)
                Report.objects.get_or_create(book=ranking.book)

        if today_ranking.count() == 0:
            payload = {
                "channel": settings.SLACK_DEFAULTS_CHANNEL,
                "icon_emoji": ":scream:",
                "username": "Something Wrong!!",
                "text": "Something Wrong!!",
            }
            try:
                urlfetch.fetch(
                    url=settings.SLACK_HOOK_URL,
                    payload=json.dumps(payload),
                    method=urlfetch.POST
                )
            except Exception as e:
                logging.info(e)
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
    except Exception as e:
        logging.info(e)



class PostToSlack(APIView):
    def post(self, request):
        """
        Slackへポスト
        ---
        parameters:
                -   name: text
                    type: string
                -   name: username
                    type: string
                -   name: channel
                    type: string
                -   name: icon
                    type: string
                -   name: url
                    type: string
        """
        text = request.POST.get("text")
        username = request.POST.get("username", settings.SLACK_DEFAULTS_USERNAME)
        icon = request.POST.get("icon", ":fire:")
        channel = request.POST.get("channel", settings.SLACK_DEFAULTS_CHANNEL)
        url = request.POST.get("url", settings.SLACK_HOOK_URL)
        payload = {
            "channel": channel,
            "icon_emoji": icon,
            "username": username,
            "link_names": 1,
            "text": text
        }
        try:
            resutls = urlfetch.fetch(
                url=url,
                payload=json.dumps(payload),
                method=urlfetch.POST
            )
            print resutls.content
        except Exception as e:
            logging.info(e)
        return Response()



def post_to_twitter(text, image_url=None):
    taskqueue.add(
        url="/book/tasks/tweet",
        params={
            u"text": text
        })



class PostToTitter(APIView):
    def post(self, request):
        """
        Twitterへポスト
        ---
        parameters:
                -   name: text
                    type: string
                -   name: image_url
                    type: string
        """
        text = request.POST.get("text")
        try:
            auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
            auth.set_access_token(settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET)
            api = tweepy.API(auth)
            api.update_status(status=text)
        except Exception as e:
            logging.info(e)
        return Response()
