"""
Test suite for the library management system API.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Book, Author, Language, Wishlist, BookRental


class BookModelTests(TestCase):
    def setUp(self):
        self.language = Language.objects.create(name="eng")
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            id=1,
            isbn="1234567890",
            title="Test Book",
            publication_year=2025,
            language=self.language
        )
        self.book.authors.add(self.author)

    def test_book_creation(self):
        """Test that a book can be created with proper attributes"""
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.publication_year, 2025)
        self.assertEqual(self.book.language.name, "eng")
        self.assertEqual(self.book.authors.first().name, "Test Author")
        self.assertTrue(self.book.is_available)


class BookAPITests(APITestCase):
    def setUp(self):
        self.language = Language.objects.create(name="eng")
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            id=1,
            isbn="1234567890",
            title="Test Book",
            publication_year=2025,
            language=self.language
        )
        self.book.authors.add(self.author)

    def test_get_books_list(self):
        """Test retrieving the list of books"""
        url = reverse('books')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_books_by_title(self):
        """Test filtering books by title"""
        url = reverse('books')
        response = self.client.get(url, {'title': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        response = self.client.get(url, {'title': 'Nonexistent'})
        self.assertEqual(len(response.data['results']), 0)

    def test_borrow_book(self):
        """Test borrowing a book"""
        url = reverse('borrow-book', kwargs={'pk': self.book.id})
        response = self.client.post(url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify book is no longer available
        self.book.refresh_from_db()
        self.assertFalse(self.book.is_available)

        # Verify rental record was created
        self.assertTrue(BookRental.objects.filter(
            book=self.book,
            borrower_email='test@example.com'
        ).exists())

    def test_return_book(self):
        """Test returning a borrowed book"""
        # First borrow the book
        BookRental.objects.create(
            book=self.book,
            borrower_email='test@example.com'
        )
        self.book.is_available = False
        self.book.save()

        url = reverse('return-book', kwargs={'pk': self.book.id})
        response = self.client.post(url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify book is available again
        self.book.refresh_from_db()
        self.assertTrue(self.book.is_available)


class WishlistTests(APITestCase):
    def setUp(self):
        self.language = Language.objects.create(name="eng")
        self.book = Book.objects.create(
            id=1,
            isbn="1234567890",
            title="Test Book",
            publication_year=2025,
            language=self.language,
            is_available=False
        )

    def test_add_to_wishlist(self):
        """Test adding a book to wishlist"""
        url = reverse('wishlist')
        data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'book_id': self.book.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify wishlist was created
        wishlist = Wishlist.objects.get(wishlist_user_email='test@example.com')
        self.assertEqual(wishlist.books.first(), self.book)

    def test_remove_from_wishlist(self):
        """Test removing a book from wishlist"""
        # First create a wishlist
        wishlist = Wishlist.objects.create(
            wishlist_user_email='test@example.com',
            wishlist_user_name='Test User'
        )
        wishlist.books.add(self.book)

        url = reverse('wishlist')
        data = {
            'email': 'test@example.com',
            'book_id': self.book.id
        }
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify book was removed from wishlist
        wishlist.refresh_from_db()
        self.assertEqual(wishlist.books.count(), 0)


class BookRentalTests(APITestCase):
    def setUp(self):
        self.language = Language.objects.create(name="eng")
        self.book = Book.objects.create(
            id=1,
            isbn="1234567890",
            title="Test Book",
            publication_year=2025,
            language=self.language
        )

    def test_rental_report(self):
        """Test generating rental report"""
        # Create some rental records
        BookRental.objects.create(
            book=self.book,
            borrower_email='test@example.com'
        )

        url = reverse('rental-report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('statistics', response.data['results'])
        self.assertIn('rental_history', response.data['results'])

    def test_rental_report_filtering(self):
        """Test filtering rental report by email"""
        BookRental.objects.create(
            book=self.book,
            borrower_email='test@example.com'
        )
        BookRental.objects.create(
            book=self.book,
            borrower_email='other@example.com'
        )

        url = reverse('rental-report')
        response = self.client.get(url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rental_history = response.data['results']['rental_history']
        self.assertEqual(len(rental_history), 1)
        self.assertEqual(rental_history[0]['borrower_email'], 'test@example.com')


class AmazonIdTests(APITestCase):
    def setUp(self):
        self.language = Language.objects.create(name="eng")
        self.book = Book.objects.create(
            id=1,
            isbn="1234567890",
            title="Test Book",
            publication_year=2025,
            language=self.language
        )

    def test_update_amazon_ids(self):
        """Test updating Amazon IDs for books"""
        url = reverse('update-amazon-ids')
        data = [{
            'book_id': self.book.id,
            'amazon_id': 'B00X12345'
        }]
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify Amazon ID was updated
        self.book.refresh_from_db()
        self.assertEqual(self.book.amazon_id, 'B00X12345')