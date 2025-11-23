from fastapi import FastAPI, HTTPException, Body, status
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from models import BookModel, UpdateBookModel
from bson import ObjectId
import os

app = FastAPI(title="Bibliothèque Numérique API")

# Configuration CORS (pour autoriser React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connexion MongoDB (utilise la variable d'env ou localhost)
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.bibliotheque
collection = db.books

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API de la Bibliothèque"}

# 1. Ajouter un livre
@app.post("/books", response_model=BookModel, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookModel = Body(...)):
    book_dict = book.dict(exclude={"id"})
    new_book = await collection.insert_one(book_dict)
    created_book = await collection.find_one({"_id": new_book.inserted_id})
    # Conversion de l'ObjectId en string pour la réponse
    created_book["_id"] = str(created_book["_id"])
    return created_book

# 2. Lister les livres + Recherche (titre, auteur, catégorie)
@app.get("/books", response_model=list[BookModel])
async def list_books(title: str = None, author: str = None, category: str = None):
    query = {}
    if title:
        query["title"] = {"$regex": title, "$options": "i"}
    if author:
        query["author"] = {"$regex": author, "$options": "i"}
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    
    books = []
    async for book in collection.find(query):
        book["_id"] = str(book["_id"])
        books.append(book)
    return books

# 3. Consulter un livre par ID
@app.get("/books/{id}", response_model=BookModel)
async def get_book(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID invalide")
    book = await collection.find_one({"_id": ObjectId(id)})
    if book is None:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    book["_id"] = str(book["_id"])
    return book

# 4. Modifier un livre
@app.put("/books/{id}", response_model=BookModel)
async def update_book(id: str, book: UpdateBookModel = Body(...)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID invalide")
    
    book_dict = {k: v for k, v in book.dict().items() if v is not None}
    
    if len(book_dict) >= 1:
        update_result = await collection.update_one({"_id": ObjectId(id)}, {"$set": book_dict})
        if update_result.modified_count == 1:
            updated_book = await collection.find_one({"_id": ObjectId(id)})
            updated_book["_id"] = str(updated_book["_id"])
            return updated_book
            
    existing_book = await collection.find_one({"_id": ObjectId(id)})
    if existing_book is None:
        raise HTTPException(status_code=404, detail="Livre non trouvé")
    existing_book["_id"] = str(existing_book["_id"])
    return existing_book

# 5. Supprimer un livre
@app.delete("/books/{id}")
async def delete_book(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID invalide")
    delete_result = await collection.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return {"message": "Livre supprimé"}
    raise HTTPException(status_code=404, detail="Livre non trouvé")