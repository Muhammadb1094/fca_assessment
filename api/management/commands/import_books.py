"""
Import books from a CSV file located at ~/assessment_documents/Backend Data.csv
"""
import csv
import os
from django.core.management.base import BaseCommand
from api.models import Author, Language, Book

class Command(BaseCommand):
    help = 'Import books from a CSV file located at assessment_documents/Backend Data.csv'

    def handle(self, *args, **kwargs):
        file_path = os.path.expanduser('assessment_documents/Backend Data.csv')
        if not os.path.exists(file_path):
            self.stderr.write(f"File not found: {file_path}")
            return

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                if row['Language'].lower():
                    language, _ = Language.objects.get_or_create(name=row['Language'].lower().strip())
                else:
                    language = None

                authors = row['Authors'].split(',')
                author_list = []
                for author_name in authors:
                    author, _ = Author.objects.get_or_create(name=author_name.strip())
                    author_list.append(author)

                book, _ = Book.objects.get_or_create(
                    id=row['Id'],
                    title=row['Title'],
                    publication_year=row['Publication Year'],
                    isbn=row['ISBN'],
                    language=language
                    )
                book.authors.set(author_list)
                book.save()
                self.stdout.write(f"Imported book: {book.title} by {', '.join(author.name for author in author_list)}")
        self.stdout.write(self.style.SUCCESS('Successfully imported books from CSV file.'))
