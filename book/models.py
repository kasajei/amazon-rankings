from __future__ import unicode_literals

import uuid

from django.db import models


def get_image_path(instance, filename=None):
    return "%s/%s/%s" % (instance.__class__.__name__, instance.id, uuid.uuid4())


class Book(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=128
    )
    title = models.CharField(
        max_length=256
    )
    url = models.URLField(

    )
    author = models.CharField(
        max_length=256
    )
    price = models.IntegerField(

    )
    star = models.FloatField(

    )
    image_url = models.URLField(

    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True
    )

    def __unicode__(self):
        return self.author + u": " + self.title


class Ranking(models.Model):
    book = models.ForeignKey(
        Book
    )
    date = models.DateField(

    )
    wish_ranking = models.IntegerField(
        null=True,
        blank=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    updated = models.DateTimeField(
        auto_now=True
    )

    def __unicode__(self):
        return str(self.date) + ": " + str(self.wish_ranking) + ": " + str(self.book_id)
