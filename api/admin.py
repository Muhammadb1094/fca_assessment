"""
Models for the API admin interface.
This file registers the Language, Author, and Book models with the Django admin site.
"""
from django.contrib import admin
from .models import Language, Author, Book, Wishlist, BookRental

# Register your models here.

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'publication_year')
    search_fields = ('title', 'authors__name', 'language__name')
    list_filter = ('language', 'publication_year')
    filter_horizontal = ('authors',)
    ordering = ('-publication_year',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('wishlist_user_email', 'wishlist_user_name', 'created_at')
    search_fields = ('wishlist_user_email', 'wishlist_user_name')
    filter_horizontal = ('books',)
    ordering = ('-created_at',)

@admin.register(BookRental)
class BookRentalAdmin(admin.ModelAdmin):
    list_display = ('book', 'borrower_email', 'borrowed_date', 'returned_date')
    search_fields = ('book__title', 'borrower_email')
    list_filter = ('borrowed_date', 'returned_date',)
    ordering = ('-borrowed_date',)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.returned_date:
            return self.readonly_fields + ('book', 'borrower_email', 'borrowed_date')
        return self.readonly_fields
