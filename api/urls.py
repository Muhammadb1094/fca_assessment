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
    path('books/<int:pk>/', BookViewSet.as_view(
        {'put': 'change_book_availability'}
        ), name='book-detail'),
]
