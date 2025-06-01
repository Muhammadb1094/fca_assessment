"""
Api views for handling book search, wishlist management, and authentication.
"""
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Book, Wishlist
from .serializers import BookSerializer, WishlistSerializer


class BookSearchAPIView(generics.ListAPIView):
    """
    API view to search for books by title or author.
    """
    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = Book.objects.all()
        title = self.request.query_params.get('title', None)
        author = self.request.query_params.get('author', None)
        is_available = self.request.query_params.get('is_available', None)

        if is_available is not None:
            is_available = is_available.lower() == 'true'
            queryset = queryset.filter(is_available=is_available)

        if title and author:
            queryset = queryset.filter(title__icontains=title, authors__name__icontains=author)
        elif title and not author:
            queryset = queryset.filter(title__icontains=title)
        elif author and not title:
            queryset = queryset.filter(authors__name__icontains=author)

        return queryset.distinct()

class WishlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user wishlists
    """
    serializer_class = WishlistSerializer

    def get_queryset(self):
        user_email = self.request.data.get('email', None)
        return Wishlist.objects.filter(wishlist_user_email=user_email)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_book(self, request):
        """Add a book to the user's wishlist"""
        book_id = request.data.get('book_id')

        try:
            book = Book.objects.get(id=book_id)
            if book.is_available:
                return Response(
                    {'error':
                        'This book is already available and cannot be added to the wishlist.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Create or get the user's wishlist
            wishlist, _ = Wishlist.objects.get_or_create(
                                    wishlist_user_email=request.data.get('email'),
                                    wishlist_user_name=request.data.get('name'))
            wishlist.books.add(book)
            return Response(
                WishlistSerializer(wishlist).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def remove_book(self, request):
        """Remove a book from the user's wishlist"""
        book_id = request.data.get('book_id')
        try:
            book = Book.objects.get(id=book_id)
            wishlist = Wishlist.objects.get(wishlist_user_email=request.data.get('email'))
            wishlist.books.remove(book)
            wishlist.save()
            return Response(
                WishlistSerializer(wishlist).data,
                status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {'error': "Book not found or not in wishlist"},
                status=status.HTTP_404_NOT_FOUND
            )
