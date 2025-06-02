"""
This module contains serializers for the API.
"""
from rest_framework import serializers
from .models import Book, Wishlist, BookRental


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


class BookRentalSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    rental_duration = serializers.SerializerMethodField()

    class Meta:
        model = BookRental
        fields = ['id', 'book_title', 'borrower_email',
                  'borrowed_date', 'returned_date', 'rental_duration']
    def get_rental_duration(self, obj):
        if obj.returned_date:
            return (obj.returned_date - obj.borrowed_date).days
        from django.utils import timezone
        return (timezone.now() - obj.borrowed_date).days


class AmazonIdUpdateSerializer(serializers.Serializer):
    """Serializer for updating Amazon IDs of books"""
    book_id = serializers.IntegerField()
    amazon_id = serializers.CharField(max_length=20)

    def validate_amazon_id(self, value):
        """Validate Amazon ID format"""
        if not value.strip():
            raise serializers.ValidationError("Amazon ID cannot be empty")
        return value.strip()

    def validate_book_id(self, value):
        """Validate that the book exists"""
        try:
            Book.objects.get(id=value)
            return value
        except Book.DoesNotExist:
            raise serializers.ValidationError("Book not found")
