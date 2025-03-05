from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = ["IncomingBook", "ReturnedBook", "ReturnedAllbooks", "BookUpdate"]

# Базовый класс "Книги", содержащий поля, которые есть во всех классах-наследниках.
class BaseBook(BaseModel):
    title: str
    author: str
    year: int

    class Config:
        orm_mode = True

# Класс для валидации входящих данных. Не содержит id, т.к. его присваивает БД.
class IncomingBook(BaseBook):
    pages: int = Field(default=150, alias="count_pages")
    seller_id: int  = Field(..., description="ID продавца, к которому относится книга")

    @field_validator("year")
    @staticmethod
    def validate_year(val: int):
        if val < 2020:
            raise PydanticCustomError("Validation error", "Year is too old!")
        return val

# Класс, валидирующий исходящие данные (возвращаем клиенту). Он уже содержит id.
class ReturnedBook(BaseBook):
    id: int
    pages: int
    seller_id: int

    class Config:
        orm_mode = True

# Класс для возврата массива объектов "Книга"
class ReturnedAllbooks(BaseModel):
    books: list[ReturnedBook]

class ReturnedBookNoSellerId(BaseModel):
    id: int
    title: str
    author: str
    year: int
    pages: int

    class Config:
        orm_mode = True

class BookUpdate(BaseModel):
    title: str
    author: str
    year: int
    pages: int

    class Config:
        orm_mode = True
