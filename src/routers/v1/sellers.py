from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.configurations import get_async_session
from src.models.sellers import Seller
from src.schemas.sellers import SellerCreate, SellerRead, SellerDetail, SellerUpdate, ReturnedAllSellers
from icecream import ic

sellers_router = APIRouter(tags=["seller"], prefix="/seller")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# 1) POST /api/v1/seller – регистрация нового продавца
@sellers_router.post("/", response_model=SellerRead, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: SellerCreate, session: DBSession):
    # Проверяем, что продавец с таким email ещё не существует
    result = await session.execute(select(Seller).where(Seller.e_mail == seller.e_mail))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Seller with this email already exists.")

    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        e_mail=seller.e_mail,
        password=seller.password  # В реальном проекте следует хэшировать пароль
    )
    session.add(new_seller)
    await session.flush()  # Чтобы сгенерировался id
    await session.refresh(new_seller)
    return new_seller


# 2) GET /api/v1/seller – получение списка всех продавцов (без password)
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    result = await session.execute(select(Seller))
    sellers = result.scalars().all()
    return {"sellers": sellers}

# 3) GET /api/v1/seller/{seller_id} – просмотр данных о конкретном продавце вместе со всеми его книгами
@sellers_router.get("/{seller_id}", response_model=SellerDetail)
async def get_seller(seller_id: int, session: DBSession):
    query = select(Seller).options(selectinload(Seller.books)).where(Seller.id == seller_id)
    result = await session.execute(query)
    seller = result.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return seller


# 4) PUT /api/v1/seller/{seller_id} – обновление данных о продавце (без изменения книг и пароля)
@sellers_router.put("/{seller_id}", response_model=SellerRead)
async def update_seller(seller_id: int, seller_update: SellerUpdate, session: DBSession):
    seller = await session.get(Seller, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    seller.first_name = seller_update.first_name
    seller.last_name = seller_update.last_name
    seller.e_mail = seller_update.e_mail
    # Поле password и книги не обновляем

    await session.flush()
    await session.refresh(seller)
    return seller


# 5) DELETE /api/v1/seller/{seller_id} – удаление продавца (и каскадное удаление его книг)
@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    seller = await session.get(Seller, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    ic(seller)  # Для отладки (можно убрать)
    await session.delete(seller)
    # Каскадное удаление книг настроено в модели (cascade="all, delete-orphan")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
