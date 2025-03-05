import pytest
from sqlalchemy import select
from src.models.books import Book
from src.models.sellers import Seller
from fastapi import status
from icecream import ic

@pytest.mark.asyncio
async def test_create_book(db_session, async_client):
    # 1. Сначала создаём продавца (seller)
    seller = Seller(
        first_name="John",
        last_name="Doe",
        e_mail="john.doe@example.com",
        password="secret"
    )
    db_session.add(seller)
    await db_session.flush()

    # 2. Отправляем запрос на создание книги, указывая seller_id
    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,  # alias для pages
        "year": 2025,
        "seller_id": seller.id
    }
    response = await async_client.post("/api/v1/books/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()
    # Достаём id созданной книги из ответа
    resp_book_id = result_data.pop("id", None)
    assert resp_book_id, "Book id not returned from endpoint"

    # Проверяем, что в ответе совпадают остальные поля
    # Если в ReturnedBook вы оставили seller_id, проверяем его тоже
    assert result_data == {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,  # так называется поле на выходе
        "year": 2025,
        "seller_id": seller.id
    }


@pytest.mark.asyncio
async def test_create_book_with_old_year(db_session, async_client):
    # Создаём продавца
    seller = Seller(
        first_name="Old",
        last_name="Seller",
        e_mail="old.seller@example.com",
        password="secret"
    )
    db_session.add(seller)
    await db_session.flush()

    # Пробуем создать книгу со старым годом
    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 1986,        # старый год (< 2020)
        "seller_id": seller.id
    }
    response = await async_client.post("/api/v1/books/", json=data)

    # Ожидаем 422, т.к. валидатор не пропускает год < 2020
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    # Сначала создаём продавца
    seller = Seller(
        first_name="Pushkin",
        last_name="A.S.",
        e_mail="pushkin@example.com",
        password="secret"
    )
    db_session.add(seller)
    await db_session.flush()

    # Создаем книги вручную
    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)
    book_2 = Book(author="Lermontov", title="Mziri", year=1997, pages=104, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/books/")
    assert response.status_code == status.HTTP_200_OK

    # Проверяем, что в ответе ровно 2 книги
    # (если в БД нет других записей, иначе тест может упасть)
    data = response.json()
    assert len(data["books"]) == 2

    # Проверяем поля у первой и второй книги
    # Если в ReturnedBook у вас есть seller_id, проверьте и его
    assert data == {
        "books": [
            {
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2001,
                "id": book.id,
                "pages": 104,
                "seller_id": seller.id
            },
            {
                "title": "Mziri",
                "author": "Lermontov",
                "year": 1997,
                "id": book_2.id,
                "pages": 104,
                "seller_id": seller.id
            },
        ]
    }


@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    # Создаём продавца
    seller = Seller(
        first_name="Pushkin",
        last_name="A.S.",
        e_mail="pushkin@example.com",
        password="secret"
    )
    db_session.add(seller)
    await db_session.flush()

    # Создаем книги вручную
    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)
    book_2 = Book(author="Lermontov", title="Mziri", year=1997, pages=104, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/books/{book.id}")
    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа
    # Если вы возвращаете seller_id, проверьте и его
    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "pages": 104,
        "id": book.id,
        "seller_id": seller.id
    }


@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    # Создаём продавца
    seller = Seller(
        first_name="Pushkin",
        last_name="A.S.",
        e_mail="pushkin@example.com",
        password="secret"
    )
    db_session.add(seller)
    await db_session.flush()

    # Создаём книгу
    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    # Обновляем поля книги
    # Если ваша схема требует seller_id при обновлении, добавьте его
    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={
            "title": "Mziri",
            "author": "Lermontov",
            "pages": 100,
            "year": 2007,
            "id": book.id,
            "seller_id": seller.id
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    updated_book = await db_session.get(Book, book.id)
    assert updated_book.title == "Mziri"
    assert updated_book.author == "Lermontov"
    assert updated_book.pages == 100
    assert updated_book.year == 2007
    assert updated_book.id == book.id


@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    # Создаём продавца
    seller = Seller(
        first_name="Lermontov",
        last_name="M.Y.",
        e_mail="lermontov@example.com",
        password="secret"
    )
    db_session.add(seller)
    await db_session.flush()

    book = Book(author="Lermontov", title="Mtziri", pages=510, year=2024, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()
    ic(book.id)

    response = await async_client.delete(f"/api/v1/books/{book.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()
    all_books = await db_session.execute(select(Book))
    res = all_books.scalars().all()

    assert len(res) == 0


@pytest.mark.asyncio
async def test_delete_book_with_invalid_book_id(db_session, async_client):
    # Создаём продавца
    seller = Seller(
        first_name="Lermontov",
        last_name="M.Y.",
        e_mail="lermontov@example.com",
        password="secret"
    )
    db_session.add(seller)
    await db_session.flush()

    book = Book(author="Lermontov", title="Mtziri", pages=510, year=2024, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id + 1}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
