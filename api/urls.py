"""
URL configuration for library api app.
"""
from django.urls import path
from api.views import BookSearchAPIView

urlpatterns = [
    path('books/', BookSearchAPIView.as_view(), name='book-search'),
]
