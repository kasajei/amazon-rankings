from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Book(models.Model):
    id = models.CharField(max_length=128)


class Ranking(models.Model):
    book = models.OneToOneField(Book)
