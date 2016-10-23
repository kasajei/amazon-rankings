# -*- coding: utf-8 -*-
from book.models import Book, Ranking
from rest_framework import serializers


class BookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'url',
            'author',
            'price',
            'star',
            'image_url',
        )


class RankingSerializer(serializers.ModelSerializer):
    book = BookSerializer()
    class Meta:
        model = Ranking
        fields = (
            "date",
            "wish_ranking",
            "book"
        )