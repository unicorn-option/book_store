from typing import List

from pydantic import BaseModel
from pydantic.types import Decimal


class AuthorItem(BaseModel):
    name: str
    nationality: str
    gender: str = 'male'


class CategoryItem(BaseModel):
    category_name: str
    parent: str = None


class BaseBookItem(BaseModel):
    book_name: str
    author: List[AuthorItem]
    publisher: str
    price: Decimal
    discount: float = 1
    category: CategoryItem
    address: str
    bar_code: str
    stock: int = 1
