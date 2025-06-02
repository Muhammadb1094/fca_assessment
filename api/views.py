"""
Api views for handling book search, wishlist management, and rentals.
"""
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from rest_framework import status, viewsets, pagination
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Book, Wishlist, BookRental
from .serializers import (
    BookSerializer, WishlistSerializer, BookRentalSerializer,
    AmazonIdUpdateSerializer
)


class CustomPagination(pagination.PageNumberPagination):
    """Custom pagination class for rental history"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing books and searching
    """
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    pagination_class = CustomPagination

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

    @action(detail=True, methods=['post'])
    def borrow(self, request, pk=None):
        """Borrow a book"""
        try:
            book = self.get_object()
            borrower_email = request.data.get('email')

            if not borrower_email:
                return Response({
                    'error': 'Email is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not book.is_available:
                return Response({
                    'error': 'Book is not available for borrowing at the moment.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create rental record
            BookRental.objects.create(
                book=book,
                borrower_email=borrower_email
            )

            # Update book availability
            book.is_available = False
            book.save()

            return Response({
                'message': f"Book '{book.title}' has been borrowed by {borrower_email}"
            }, status=status.HTTP_200_OK)

        except Book.DoesNotExist:
            return Response({
                'error': 'Book not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """Return a borrowed book"""
        try:
            book = self.get_object()
            borrower_email = request.data.get('email')

            if not borrower_email:
                return Response({
                    'error': 'Email is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            if book.is_available:
                return Response({
                    'error': 'Book is already returned and available for borrowing.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update rental record
            rental = BookRental.objects.filter(
                book=book,
                borrower_email=borrower_email,
                returned_date__isnull=True
            ).first()

            if not rental:
                return Response({
                    'error': 'No active rental found for this book and email'
                }, status=status.HTTP_400_BAD_REQUEST)

            rental.returned_date = timezone.now()
            rental.save()

            # Update book availability
            book.is_available = True
            book.save()

            return Response({
                'message': f"Book '{book.title}' has been returned by {borrower_email}"
            }, status=status.HTTP_200_OK)

        except Book.DoesNotExist:
            return Response({
                'error': 'Book not found'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def rental_report(self, request):
        """Get a detailed report of all book rentals with statistics"""
        # Get current date and time
        now = timezone.now()
        start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_week = now - timedelta(days=now.weekday())

        # Base queryset
        rentals = BookRental.objects.all()
        
        # Filter by email if provided
        email = request.query_params.get('email')
        if email:
            rentals = rentals.filter(borrower_email=email)

        # Filter by status if provided
        status_param = request.query_params.get('status')
        if status_param:
            if status_param.lower() == 'active':
                rentals = rentals.filter(returned_date__isnull=True)
            elif status_param.lower() == 'returned':
                rentals = rentals.filter(returned_date__isnull=False)

        # Calculate statistics
        stats = {
            'total_rentals': rentals.count(),
            'currently_rented': rentals.filter(returned_date__isnull=True).count(),
            'this_year_rentals': rentals.filter(borrowed_date__gte=start_of_year).count(),
            'this_month_rentals': rentals.filter(borrowed_date__gte=start_of_month).count(),
            'this_week_rentals': rentals.filter(borrowed_date__gte=start_of_week).count(),
            'average_rental_days': 0  # Will be calculated below
        }

        # Calculate average rental duration for completed rentals
        completed_rentals = rentals.filter(returned_date__isnull=False)
        if completed_rentals.exists():
            total_days = 0
            for rental in completed_rentals:
                duration = (rental.returned_date - rental.borrowed_date).days
                total_days += duration
            stats['average_rental_days'] = total_days / completed_rentals.count()

        # Paginate the rental history
        paginator = self.pagination_class()
        paginated_rentals = paginator.paginate_queryset(rentals.order_by('-borrowed_date'), request)
        rental_data = BookRentalSerializer(paginated_rentals, many=True).data

        # Prepare the response
        response_data = {
            'statistics': stats,
            'rental_history': rental_data
        }

        return paginator.get_paginated_response(response_data)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def update_amazon_ids(self, request):
        """Update Amazon IDs for multiple books"""
        serializer = AmazonIdUpdateSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated_books = []
        errors = []

        for item in serializer.validated_data:
            try:
                book = Book.objects.get(id=item['book_id'])
                book.amazon_id = item['amazon_id']
                book.save()
                updated_books.append({
                    'book_id': book.id,
                    'title': book.title,
                    'amazon_id': book.amazon_id
                })
            except Book.DoesNotExist:
                errors.append({
                    'book_id': item['book_id'],
                    'error': 'Book not found'
                })

        return Response({
            'updated_books': updated_books,
            'errors': errors
        }, status=status.HTTP_200_OK)


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
