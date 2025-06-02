"""
URL configuration for library api app.
"""
from django.urls import path

from api.views import BookViewSet, WishlistViewSet

urlpatterns = [
    path('wishlist/', WishlistViewSet.as_view(
        {'post': 'add_book', 'delete': 'remove_book'}
        ), name='wishlist'),
    path('books/', BookViewSet.as_view(
        {'get': 'list'}
        ), name='books'),
    path('books/<int:pk>/borrow/', BookViewSet.as_view(
        {'post': 'borrow'}
        ), name='borrow-book'),
    path('books/<int:pk>/return/', BookViewSet.as_view(
        {'post': 'return_book'}
        ), name='return-book'),
    path('books/rental-report/', BookViewSet.as_view(
        {'get': 'rental_report'}
        ), name='rental-report'),
]
