"""
Api views for handling book search, wishlist management, and authentication.
"""
from rest_framework import generics

from .models import Book
from .serializers import BookSerializer


class BookSearchAPIView(generics.ListAPIView):
    """
    API view to search for books by title or author.
    """
    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = Book.objects.all()
        title = self.request.query_params.get('title', None)
        author = self.request.query_params.get('author', None)

        if title and author:
            queryset = queryset.filter(title__icontains=title, authors__name__icontains=author)
        elif title and not author:
            queryset = queryset.filter(title__icontains=title)
        elif author and not title:
            queryset = queryset.filter(authors__name__icontains=author)

        return queryset.distinct()
