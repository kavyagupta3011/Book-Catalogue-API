from flask import Flask, request, jsonify, make_response, url_for, abort

app=Flask(__name__)

# In-memory "database" of books (sample data)
books = [
    {
        "id": 1,
        "title":"Pride and Prejudice",
        "author":"Jane Austen",
        "year":1813,
        "isbn":"1111111111"
    },
    {
        "id": 2,
        "title":"1984",
        "author":"George Orwell",
        "year":1949,
        "isbn":"2222222222"
    }
]

# Auto-increment id helper
next_id = 3


def find_book(book_id):
    """Return book dict if present else None."""
    return next((b for b in books if b["id"] == book_id), None)


@app.errorhandler(404)
def not_found(error):
    """Return JSON 404."""
    return make_response(jsonify({"error": "Resource not found"}), 404)


@app.errorhandler(400)
def bad_request(error):
    """Return JSON 400."""
    return make_response(jsonify({"error": "Bad request"}), 400)


# GET /books
# Returns list of books. Supports optional query params:author (string), title  (string, partial match)
# Example: /books?author=Orwell
@app.route("/books", methods=["GET"])
def get_books():
    author=request.args.get("author")
    title=request.args.get("title")

    result=books

    if author:
        result=[b for b in result if author.lower() in b["author"].lower()]
    if title:
        result=[b for b in result if title.lower() in b["title"].lower()]

    return jsonify(result), 200


#GET /books/<id>
#Returns a single book by id.
@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book=find_book(book_id)
    if not book:
        abort(404)
    return jsonify(book), 200


# POST /books
# Create a new book. JSON body must include at least 'title' and 'author'.
# Optional: year (int), isbn (string).
# Returns 201 with created book.
@app.route("/books", methods=["POST"])
def create_book():
    global next_id

    if not request.is_json:
        abort(400)

    data=request.get_json()
    title=data.get("title")
    author=data.get("author")
    year=data.get("year")
    isbn=data.get("isbn")

    if not title or not author:
        # title and author are required for creation
        return make_response(jsonify({"error": "Missing 'title' or 'author'"}), 400)

    new_book = {
        "id": next_id,
        "title": title,
        "author": author,
        "year": year,
        "isbn": isbn
    }
    books.append(new_book)
    next_id += 1

    # Location header points to the new resource
    location = url_for("get_book", book_id=new_book["id"])
    return make_response(jsonify(new_book), 201, {"Location": location})


# PUT /books/<id>
# Update an existing book (full replacement of fields provided).
# If a field is omitted, it will remain unchanged. Returns updated book.
@app.route("/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    if not request.is_json:
        abort(400)
    book = find_book(book_id)
    if not book:
        abort(404)

    data=request.get_json()
    # Update only allowed fields if provided
    for field in ("title", "author", "year", "isbn"):
        if field in data:
            book[field] = data[field]

    return jsonify(book), 200


# DELETE /books/<id>
# Delete a book by id. Returns 204 No Content on success.
@app.route("/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book=find_book(book_id)
    if not book:
        abort(404)
    books.remove(book)
    return "", 204


if __name__ == "__main__":
    # Run server on localhost:5000
    app.run(host="127.0.0.1", port=5000, debug=True)
