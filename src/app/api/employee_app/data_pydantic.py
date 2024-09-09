from typing import List

from pydantic import BaseModel

from src.app.api.book_app.data_pydantic import AuthorItem, BaseBookItem, CategoryItem


class BaseEmployeeItem(BaseModel):
    phone: str
    gender: str = 'male'


class EmployeeItem(BaseEmployeeItem):
    require_pass: str


class BooksItem(BaseModel):
    book_data: List[BaseBookItem]


class AuthorsItem(BaseModel):
    author_data: List[AuthorItem]


class CategoriesItem(BaseModel):
    category_data: List[CategoryItem]
