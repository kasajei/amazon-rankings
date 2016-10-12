# -*- coding: utf-8 -*-
from book.models import Book
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