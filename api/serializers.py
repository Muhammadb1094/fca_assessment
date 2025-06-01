"""
This module contains serializers for the API.
"""
from rest_framework import serializers
from .models import Book, Wishlist


class BookSerializer(serializers.ModelSerializer):
    authors = serializers.StringRelatedField(many=True)
    language = serializers.StringRelatedField()

    class Meta:
        model = Book
        exclude = ['created_at', 'updated_at']


class WishlistSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'books']
