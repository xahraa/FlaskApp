from pymongo import MongoClient

Client = MongoClient("mongodb://flaskmongodbapp:7tnU247b5SSCl33HQJPF4WJHtReOTc7BH1jMieDiFJqPMIr2vOLmKsBAWEe44zrT8pvr4mxpicu4ACDbbOzUEQ==@flaskmongodbapp.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@flaskmongodbapp@")
db = Client["bookstore"]

class Publisher:
    def __init__(self, name, id, _id=None):
        self.id = id
        self._id = _id
        self.name = name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Author:
    def __init__(self, identityNo, firstName, lastName):
        self.identityNo = identityNo
        self.firstName = firstName
        self.lastName = lastName

    def to_dict(self):
        return {
            "identityNo": self.identityNo,
            "firstName": self.firstName,
            "lastName": self.lastName,
        }


class Book:
    def __init__(self, isbn, title, year, price, page, category, coverPhoto, publisher, author, _id=None):
        self._id = _id
        self.isbn = isbn
        self.title = title
        self.year = year
        self.price = price
        self.page = page
        self.category = category
        self.coverPhoto = coverPhoto
        if isinstance(publisher, dict):
            self.publisher = Publisher(**publisher)
        else:
            self.publisher = publisher      
        self.author = Author(**author) if isinstance(author, dict) else author
    
    def to_dict(self):
        return {
            "isbn": self.isbn,
            "title": self.title,
            "year": self.year,
            "price": self.price,
            "page": self.page,
            "category": self.category,
            "coverPhoto": self.coverPhoto,
            "publisher": self.publisher.to_dict() if self.publisher else None,
            "author": self.author.to_dict() if self.author else None,
        }


    @classmethod
    def find_by_isbn(cls, isbn):
        """Find a book by ISBN."""
        return db.books.find_one({"isbn": isbn})


    def save(self):
        book_data = self.to_dict()
        existing_book = Book.find_by_isbn(self.isbn)
        if existing_book:
            raise ValueError("A book with this ISBN already exists")
        return db.books.insert_one(book_data)

    @staticmethod
    def list_all_books(page=1, limit=10, sort_by='title', order=1):
        """List all books with pagination and sorting."""
        books = []
        skip = (page - 1) * limit

        # Adjusting order for sorting (1 for ascending, -1 for descending)
        order = -1 if order.lower() == 'desc' else 1

        for book_data in db.books.find().skip(skip).limit(limit).sort(sort_by, order):
            # Map 'coverPhoto' from book_data to 'cover_photo'
            # Extract _id if present and remove from book_data to avoid duplication
            _id = book_data.pop('_id', None)
            book = Book(_id=_id, **book_data)
            books.append(book)
        return books
    
    @staticmethod
    def delete_book(isbn):
       """Delete a book by ISBN and return True if successful, False otherwise."""
       result = db.books.delete_one({'isbn': isbn})
       return result.deleted_count > 0


    @staticmethod
    def get_book_details(isbn):
        """Get details of a specific book."""
        return Book.find_by_isbn(isbn)

    @staticmethod
    def add_book(book_data):
        """Add a new book."""
        # Validate and convert data
        try:
            book_data['year'] = int(book_data['year'])
            book_data['page'] = int(book_data['page'])
            book_data['price'] = float(book_data['price'])
        except ValueError as e:
            raise ValueError(f"Invalid data format: {e}")

        # Check if book exists
        if Book.find_by_isbn(book_data["isbn"]):
            raise ValueError("Book with this ISBN already exists")
        
        # Handle nested objects - Publisher
        publisher_data = book_data.get("publisher")
        if isinstance(publisher_data, dict):
           publisher = Publisher(**publisher_data)
        elif isinstance(publisher_data, Publisher):
           publisher = publisher_data
        else:
           raise ValueError("Invalid publisher data")

        # Handle nested objects - Author
        author_data = book_data.get("author")
        if isinstance(author_data, dict):
          author = Author(**author_data)
        elif isinstance(author_data, Author):
           author = author_data
        else:
           raise ValueError("Invalid author data")

        # Create new book instance with the constructed Publisher and Author
        new_book = Book(
            isbn=book_data["isbn"],
            title=book_data["title"],
            year=book_data["year"],
            price=book_data["price"],
            page=book_data["page"],
            category=book_data["category"],
            coverPhoto=book_data["coverPhoto"],
            publisher =publisher,
            author=author
        )

        # Save the book
        try:
            return new_book.save()
        except Exception as e:
            # Log error and re-raise
            # log.error(f"Error adding book: {e}")
            raise

    


    @staticmethod
    def update_book(isbn, update_data): 
        """Update a book's details."""
        if not Book.find_by_isbn(isbn):
           raise ValueError("Book not found")
 
    # Convert string numbers to integers
        if 'year' in update_data:
           update_data['year'] = int(update_data['year'])
        if 'page' in update_data:
           update_data['page'] = int(update_data['page'])
           update_data.pop('category', None)


        updated_result = db.books.update_one({'isbn': isbn}, {'$set': update_data})
        if updated_result.matched_count == 0:
           raise ValueError("No matching book found to update")
        return updated_result


    
    @staticmethod
    def search_books(query_params, page=1, limit=10):
         """Search for books by various criteria."""
         search_query = {}
    
         if 'query' in query_params and query_params['query']:
             regex_query = {"$regex": query_params['query'], "$options": "i"}  # Case-insensitive partial match
             search_query = {
                 "$or": [
                {"title": regex_query},
                {"isbn": regex_query},
                {"author.firstName": regex_query},
                {"author.lastName": regex_query},
                {"category": regex_query}
            ]
        }
    
         skip = (page - 1) * limit
         books_cursor = db.books.find(search_query).skip(skip).limit(limit)
         books = [Book(_id=str(book_data.pop('_id', None)), **book_data) for book_data in books_cursor]

         return books
