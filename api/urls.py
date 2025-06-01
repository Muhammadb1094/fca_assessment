"""
URL configuration for library api app.
"""
from django.urls import path

from api.views import BookSearchAPIView, WishlistViewSet

urlpatterns = [
    path('books/', BookSearchAPIView.as_view(), name='book-search'),
    path('wishlist/', WishlistViewSet.as_view(
        {'post': 'add_book', 'delete': 'remove_book'}), name='wishlist'),
]
