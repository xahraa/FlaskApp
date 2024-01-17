from flask import Flask, request, render_template, redirect, url_for
from model import Book
from math import ceil
from pymongo import MongoClient

Client = MongoClient("mongodb://flaskmongodbapp:7tnU247b5SSCl33HQJPF4WJHtReOTc7BH1jMieDiFJqPMIr2vOLmKsBAWEe44zrT8pvr4mxpicu4ACDbbOzUEQ==@flaskmongodbapp.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@flaskmongodbapp@")
db = Client["bookstore"]
app = Flask(__name__)

from math import ceil

@app.route('/books', methods=['GET'])
def list_all_books():
    try:
        # Retrieve query parameters for pagination and sorting
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        sort_by = request.args.get('sort', 'title')
        order = request.args.get('order', 'asc')

        books = Book.list_all_books(page, limit, sort_by, order)

        # Calculate the total number of pages
        total_books = db.books.count_documents({})
        total_pages = ceil(total_books / limit)

        return render_template('list_books.html', books=books, current_page=page, total_pages=total_pages, limit=limit)
    except Exception as e:
        return str(e), 500



# Get book details
@app.route('/books/<isbn>', methods=['GET'])
def get_book(isbn):
    try:
        book = Book.get_book_details(isbn)
        return render_template('book_detail.html', book=book) if book else ('Book not found', 404)
    except Exception as e:
        return str(e), 500

# Add a new book
@app.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        try:
            book_data = request.form.to_dict()
            # Handle nested objects: publisher and author
            # Note: This assumes your form has fields prefixed with 'publisher_' and 'author_'
            publisher_data = {key.split('_', 1)[1]: value for key, value in book_data.items() if key.startswith('publisher_')}
            author_data = {key.split('_', 1)[1]: value for key, value in book_data.items() if key.startswith('author_')}

            # Remove these fields from the main book_data
            book_data = {key: value for key, value in book_data.items() if not key.startswith('publisher_') and not key.startswith('author_')}

            # Add the nested objects back to the book_data
            book_data['publisher'] = publisher_data
            book_data['author'] = author_data

            Book.add_book(book_data)
            return redirect(url_for('list_all_books'))
        except ValueError as e:
            return str(e), 400
        except Exception as e:
            return str(e), 500
    return render_template('add_book.html')



@app.route('/books/<isbn>/update', methods=['GET', 'POST'])
def update_book(isbn):
    try:
        if request.method == 'POST':
            update_data = request.form.to_dict()

            # Extract publisher and author data
            publisher_data = {
                "id": update_data.pop('publisher_id', None),
                "name": update_data.pop('publisher_name', None)
            }
            author_data = {
                "identityNo": update_data.pop('author_identityNo', None),
                "firstName": update_data.pop('author_firstName', None),
                "lastName": update_data.pop('author_lastName', None)
            }

            # Update book details
            book_data = {
                "isbn": isbn,
                "title": update_data.get('title'),
                "year": update_data.get('year'),
                "price": update_data.get('price'),
                "page": update_data.get('page'),
                "category": update_data.get('category'),
                "coverPhoto": update_data.get('coverPhoto'),
                "publisher": publisher_data,
                "author": author_data
            }
            Book.update_book(isbn, book_data)
            return redirect(url_for('get_book', isbn=isbn))

        # Retrieve book details for editing
        book = Book.get_book_details(isbn)
        if book:
            return render_template('update_book.html', book=book)
        else:
            return 'Book not found', 404

    except ValueError as e:
        return str(e), 400
    except Exception as e:
        return str(e), 500



@app.route('/books/<isbn>/delete', methods=['GET', 'POST'])
def delete_book_route(isbn):
    book_deleted = Book.delete_book(isbn)
    if not book_deleted:
        pass
    return redirect(url_for('list_all_books'))


@app.route('/books/search', methods=['GET'])
def search_books():
    try:
        query_params = request.args.to_dict()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        books = Book.search_books(query_params, page, limit)

        # Adjusting the count_documents query to match the search_books method
        if 'query' in query_params and query_params['query']:
            regex_query = {"$regex": query_params['query'], "$options": "i"}
            count_query = {
                "$or": [
                    {"title": regex_query},
                    {"isbn": regex_query},
                    {"author.firstName": regex_query},
                    {"author.lastName": regex_query},
                    {"category": regex_query}
                ]
            }
        else:
            count_query = {}

        total_books = db.books.count_documents(count_query)
        total_pages = ceil(total_books / limit)

        return render_template('search_books.html', books=books, query=query_params, current_page=page, total_pages=total_pages, limit=limit)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
    
