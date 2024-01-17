
from model import Book

# Example book details
isbn = "45365645"
title = "hi"
year = 2022
price = 29.99
page = 300
category = "Drama"
coverPhoto = "http://example.com/cover.jpg"
publisher = {"id": 5, "name": "Example Publisher"}
author = {"identityNo": 10, "firstName": "John", "lastName": "Doe"}


# Create a Book instance
book_to_add = Book(isbn, title, year, price, page, category, coverPhoto, publisher, author)

# Save the book to the database
result = Book.add_book(book_to_add.to_dict())

# Check if the book was successfully added
if result:
    print("Book was successfully added with ID:", result.inserted_id)
else:
    print("An error occurred while adding the book.")

