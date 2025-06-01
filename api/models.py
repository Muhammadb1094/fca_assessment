"""
This module defines the models for the library management system.
"""
from django.db import models
from isbn_field import ISBNField


class Author(models.Model):
    """
    Author Model
    Represents an author with a name and timestamps for creation and updates.
    Attributes:
        name (str): The name of the author, limited to 200 characters.
        created_at (datetime): The timestamp when the author record was created.
        updated_at (datetime): The timestamp when the author record was last updated.
    Meta:
        ordering (list): Orders authors by creation date in descending order.
        verbose_name (str): Human-readable singular name for the model.
        verbose_name_plural (str): Human-readable plural name for the model.
    Methods:
        __str__(): Returns the string representation of the author, which is the author's name.
    """
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for model configuration, including ordering and verbose names.
        """
        ordering = ['-created_at']
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return f"{self.name}"

class Language(models.Model):
    """
    Represents a language entity in the database.
    Attributes:
        name (str): The name of the language, stored as a CharField with a maximum length of 200 characters.
        created_at (datetime): The timestamp when the language record was created, automatically set on creation.
        updated_at (datetime): The timestamp when the language record was last updated, automatically updated on modification.
    Meta:
        ordering (list): Specifies the default ordering of language records by creation date in descending order.
        verbose_name (str): A human-readable singular name for the model.
        verbose_name_plural (str): A human-readable plural name for the model.
    Methods:
        __str__(): Returns the string representation of the language, which is its name.
    """

    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for model configuration, including ordering and verbose names.
        """
        ordering = ['-created_at']
        verbose_name = "Language"
        verbose_name_plural = "Languages"

    def __str__(self):
        return f"{self.name}"

class Book(models.Model):
    """
    Represents a book in the library management system.
    Attributes:
        id (int): Unique identifier for the book, automatically generated.
        isbn (str): International Standard Book Number, unique for each book.
        title (str): Title of the book, limited to 255 characters.
        authors (ManyToManyField): Relationship to Author model, allowing multiple authors per book.
        publication_year (int): Year the book was published, stored as a positive integer.
        language (ForeignKey): Relationship to Language model, indicating the language of the book.
        is_available (bool): Indicates if the book is currently available
        created_at (datetime): Timestamp when the book record was created, automatically set on creation.
        updated_at (datetime): Timestamp when the book record was last updated, automatically updated on modification.
    Meta:
        ordering (list): Specifies the default ordering of book records by creation date in descending order.
        verbose_name (str): A human-readable singular name for the model.
        verbose_name_plural (str): A human-readable plural name for the model.
    Methods:
        __str__(): Returns the string representation of the book, which includes its ID, title, and ISBN.
    """
    id = models.BigIntegerField(unique=True, primary_key=True)
    isbn = ISBNField(unique=True, verbose_name="ISBN")
    title = models.CharField(max_length=255)
    authors = models.ManyToManyField(Author, related_name='books')
    publication_year = models.IntegerField()
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='books',
                                 null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for model configuration, including ordering and verbose names.
        """
        ordering = ['-created_at']
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.id}. {self.title} ({self.isbn})"
