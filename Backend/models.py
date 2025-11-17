from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

# Helper pour gérer les ID MongoDB
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class BookModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    author: str
    category: str

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "title": "Le Petit Prince",
                "author": "Antoine de Saint-Exupéry",
                "category": "Roman"
            }
        }

class UpdateBookModel(BaseModel):
    title: Optional[str]
    author: Optional[str]
    category: Optional[str]