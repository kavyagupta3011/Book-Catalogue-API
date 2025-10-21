from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Library Catalog Service")

# In-memory catalog (temporary storage)
# - Using a simple Python list of dictionaries for storage
# - Each book has: id (int), title (str), author (str)
# - This is NOT persistent (data will reset if server restarts)
catalog = [
    {"id": 1, "title": "Computer Networks", "author": "Andrew S."},
    {"id": 2, "title": "Database Concepts", "author": "R. Elmasri"},
    {"id": 3, "title": "Algorithms Unlocked", "author": "T. Cormen"}
]

# Pydantic model for input validation
# Only 'title' and 'author' are required fields when adding/updating books
# - Ensures any data coming from client matches this structure
# - 'title' and 'author' must both be strings
# - If request body is invalid, FastAPI will automatically return a 422 error
class BookItem(BaseModel):
    title: str
    author: str

# GET: return all books
# response_model=List[dict] → ensures FastAPI outputs a list of dictionaries
@app.get("/books", response_model=List[dict])
def list_books():
    return catalog

# GET: return single book by id
# {item_id} is a path parameter automatically converted to int
@app.get("/books/{item_id}", response_model=dict)
def retrieve_book(item_id: int):
    item = next((x for x in catalog if x["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Book not found")
    return item

# POST: add a new book
# status_code=201 → indicates successful resource creation
# - The request body must match the BookItem model (validated automatically)
# - response_model=dict → return the newly created book as JSON
# - status_code=201 → correct HTTP status for resource creation
@app.post("/books", response_model=dict, status_code=201)
def create_entry(entry: BookItem):
    new_id = max(x["id"] for x in catalog) + 1 if catalog else 1
    new_record = {"id": new_id, "title": entry.title, "author": entry.author}
    catalog.append(new_record)
    return new_record

# PUT: update an existing book
# - The client must send a JSON body matching BookItem schema
# - If the book exists, update its fields
# - If not found, return 404
@app.put("/books/{item_id}", response_model=dict)
def update_book(item_id: int, payload: BookItem):
    for rec in catalog:
        if rec["id"] == item_id:
            # preserve existing values if empty strings are passed (behavior kept)
            rec["title"] = payload.title or rec["title"]
            rec["author"] = payload.author or rec["author"]
            return rec
    raise HTTPException(status_code=404, detail="Book not found")

# DELETE: remove a book
# - Deletes the record if found
# - If not found, returns 404
# - response_model=dict → returns a confirmation message
@app.delete("/books/{item_id}", response_model=dict)
def remove_book(item_id: int):
    global catalog
    for rec in catalog:
        if rec["id"] == item_id:
            catalog = [c for c in catalog if c["id"] != item_id]
            return {"message": f"Book {item_id} deleted"}
    raise HTTPException(status_code=404, detail="Book not found")
