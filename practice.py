# ============================================
# FASTAPI PRACTICE EXERCISES
# ============================================
# Instructions:
# 1. Try to write each exercise WITHOUT looking at main.py
# 2. Run with: uvicorn practice:app --reload --port 8001
# 3. Test in browser: http://127.0.0.1:8001/docs
# ============================================
from ...... import STATUS
#to get raise http exception and server status
from fastapi import FastAPI

app = FastAPI()

# ============================================
# EXERCISE 1: Basic GET endpoint
# ============================================
# Create a GET endpoint at "/hello" that returns {"message": "Hello World"}
# YOUR CODE HERE:


@app.get("/hello")
def greetings():
    return{"message":"hello world"}

# ============================================
# EXERCISE 2: Path Parameter
# ============================================
# Create GET "/greet/{name}" that returns {"message": "Hello, {name}!"}
# Example: /greet/Bob → {"message": "Hello, Bob!"}
# YOUR CODE HERE:

@app.get("/greet/{name}")
def greetings_with_path(names:str):
    return{"message":"hello "+{names}}



# ============================================
# EXERCISE 3: Pydantic Model + POST
# ============================================
# Create a Pydantic model called "Book" with: title (str), author (str), pages (int)
# Create POST "/books" that accepts a Book and returns {"status": "added", "book": ...}
# YOUR CODE HERE:
class Book:
    title:str
    author:str
    pages:int
@app.post("/books")
def read_books(stitle:Book.title,sauthor:Book.author,spages:int:Book.pages):
    returns{"status":"added","book":"idk","author":sauthor}








# ============================================
# EXERCISE 4: HTTPException
# ============================================
# Create GET "/items/{item_id}"
# If item_id > 100, return the item
# If item_id <= 100, raise HTTPException with 404 and detail "Item not found"
# YOUR CODE HERE:
@app.get("/items/{item_id}")
def checkid(id:int):
    if item_id>100:
        reutrn item_id
    raise HTTPEException {status_code:404,details:"item not found"}




# ============================================
# EXERCISE 5: Query Parameters
# ============================================
# Create GET "/search" with optional query param "q" (string)
# Return {"query": q} or {"query": "nothing"} if q is None
# YOUR CODE HERE:


@app.get("/search/{q}")
i give up this one

# ============================================
# ANSWERS ARE IN: practice_answers.py (I'll create it if you ask)
# ============================================
