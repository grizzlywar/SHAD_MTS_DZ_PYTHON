from pydantic import BaseModel, EmailStr, Field
from typing import List
from src.schemas.books import ReturnedBookNoSellerId  # Эта схема должна быть определена в вашем проекте

# Базовая схема с общими полями (без пароля)
class SellerBase(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr

    class Config:
        orm_mode = True

# Схема для создания продавца – включает пароль
class SellerCreate(SellerBase):
    password: str

# Схема для возврата данных о продавце (без поля password)
class SellerRead(SellerBase):
    id: int = Field(..., example=1)

# Схема для детального представления продавца – включает список книг
class SellerDetail(SellerRead):
    books: List[ReturnedBookNoSellerId] = Field(default_factory=list)

# Схема для обновления данных о продавце (без изменения пароля и книг)
class SellerUpdate(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr

    class Config:
        orm_mode = True

class ReturnedAllSellers(BaseModel):
    sellers: List[SellerRead]

    class Config:
        orm_mode = True
