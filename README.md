# Library Management System API

A Django REST framework based API for managing a library system with book rentals, wishlists, and Amazon affiliate integration.

## Features

- Book management with filtering and search capabilities
- Book rental system with borrowing and return functionality
- Wishlist system for unavailable books
- Rental statistics and reporting
- Amazon affiliate ID management
- Comprehensive test suite

## Prerequisites

- Python 3.13+
- pip (Python package manager)
- virtualenv (recommended)

## Setup

1. Clone the repository and create a virtual environment:
```bash
git clone <repository-url>
cd fca_assessment
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Import initial book data:
```bash
python manage.py import_books
```

5. Run the development server:
```bash
python manage.py runserver
```

## Running Tests

To run the test suite:
```bash
python manage.py test api
```

## API Endpoints

### Books

#### List Books
- **GET** `/api/books/`
- Query Parameters:
  - `title`: Filter by book title
  - `author`: Filter by author name
  - `is_available`: Filter by availability (true/false)

#### Borrow Book
- **POST** `/api/books/{book_id}/borrow/`
- Request Body:
```json
{
    "email": "borrower@example.com"
}
```

#### Return Book
- **POST** `/api/books/{book_id}/return/`
- Request Body:
```json
{
    "email": "borrower@example.com"
}
```

#### Update Amazon IDs
- **POST** `/api/books/update-amazon-ids/`
- Request Body:
```json
[
    {
        "book_id": 1,
        "amazon_id": "B00X12345"
    },
    {
        "book_id": 2,
        "amazon_id": "B00X67890"
    }
]
```

### Rental Reports

#### Get Rental Statistics
- **GET** `/api/books/rental-report/`
- Query Parameters:
  - `email`: Filter by borrower email
  - `status`: Filter by rental status (active/returned)
  - `page`: Page number for pagination
  - `page_size`: Number of items per page (default: 10, max: 100)

Response includes:
- Statistics for total rentals
- Current rentals
- This year/month/week rentals
- Average rental duration
- Paginated rental history

### Wishlists

#### Add to Wishlist
- **POST** `/api/wishlist/`
- Request Body:
```json
{
    "email": "user@example.com",
    "name": "User Name",
    "book_id": 1
}
```

#### Remove from Wishlist
- **DELETE** `/api/wishlist/`
- Request Body:
```json
{
    "email": "user@example.com",
    "book_id": 1
}
```

## Data Model

### Book
- id (BigInteger, Primary Key)
- isbn (ISBN, Unique)
- title (String)
- authors (Many-to-Many relationship with Author)
- publication_year (Integer)
- language (Foreign Key to Language)
- is_available (Boolean)
- amazon_id (String, optional)

### BookRental
- book (Foreign Key to Book)
- borrower_email (Email)
- borrowed_date (DateTime)
- returned_date (DateTime, nullable)

### Wishlist
- wishlist_user_email (Email)
- wishlist_user_name (String)
- books (Many-to-Many relationship with Book)

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Success
- 400: Bad Request (invalid input)
- 404: Not Found
- 500: Server Error

Error responses include a message explaining the error.

## Data Import Format

The system expects a CSV file with the following columns:
- Id
- ISBN
- Authors (comma-separated)
- Publication Year
- Title
- Language

The import command will handle creating all necessary related objects (authors, languages) automatically.

## Development

### Running Tests
Tests are organized by functionality:
- BookTests: Basic book operations
- BookRentalTests: Rental functionality
- WishlistTests: Wishlist management
- AmazonIdUpdateTests: Amazon affiliate ID management

Run specific test classes:
```bash
python manage.py test api.tests.BookTests
python manage.py test api.tests.BookRentalTests
```