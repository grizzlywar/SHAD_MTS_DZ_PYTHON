import pytest
from fastapi import status
from src.models.sellers import Seller


# Тест для POST /api/v1/seller/ – регистрация нового продавца
@pytest.mark.asyncio
async def test_create_seller(async_client, db_session):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe@example.com",
        "password": "secret"
    }
    response = await async_client.post("/api/v1/seller/", json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()
    assert "id" in result, "Seller id not returned"
    seller_id = result.pop("id")
    assert result == {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe@example.com"
    }


# Тест для GET /api/v1/seller/ – получение списка всех продавцов
@pytest.mark.asyncio
async def test_get_all_sellers(async_client, db_session):
    # Создаем двух продавцов напрямую через модель
    seller1 = Seller(first_name="Alice", last_name="Smith", e_mail="alice@example.com", password="secret")
    seller2 = Seller(first_name="Bob", last_name="Jones", e_mail="bob@example.com", password="secret")
    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/seller/")
    assert response.status_code == status.HTTP_200_OK

    # Получаем словарь с ключом "sellers"
    data = response.json()
    sellers = data["sellers"]

    # Проверяем, что продавцы созданы
    emails = [s["e_mail"] for s in sellers]
    assert "alice@example.com" in emails
    assert "bob@example.com" in emails


# Тест для GET /api/v1/seller/{seller_id} – получение конкретного продавца с книгами
@pytest.mark.asyncio
async def test_get_single_seller(async_client, db_session):
    # Создаем продавца (без книг)
    seller = Seller(first_name="Carol", last_name="White", e_mail="carol@example.com", password="secret")
    db_session.add(seller)
    await db_session.flush()
    seller_id = seller.id

    response = await async_client.get(f"/api/v1/seller/{seller_id}")
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] == seller_id
    assert result["first_name"] == "Carol"
    assert result["last_name"] == "White"
    assert result["e_mail"] == "carol@example.com"
    # Поле books должно быть списком (возможно пустым)
    assert isinstance(result["books"], list)


# Тест для PUT /api/v1/seller/{seller_id} – обновление продавца (без изменения книг и пароля)
@pytest.mark.asyncio
async def test_update_seller(async_client, db_session):
    # Создаем продавца
    seller = Seller(first_name="David", last_name="Brown", e_mail="david@example.com", password="secret")
    db_session.add(seller)
    await db_session.flush()
    seller_id = seller.id

    update_data = {
        "first_name": "Dave",
        "last_name": "Brown",
        "e_mail": "dave.brown@example.com"
    }
    response = await async_client.put(f"/api/v1/seller/{seller_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] == seller_id
    assert result["first_name"] == "Dave"
    assert result["last_name"] == "Brown"
    assert result["e_mail"] == "dave.brown@example.com"


# Тест для DELETE /api/v1/seller/{seller_id} – удаление продавца
@pytest.mark.asyncio
async def test_delete_seller(async_client, db_session):
    # Создаем продавца
    seller = Seller(first_name="Eve", last_name="Black", e_mail="eve@example.com", password="secret")
    db_session.add(seller)
    await db_session.flush()
    seller_id = seller.id

    response = await async_client.delete(f"/api/v1/seller/{seller_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Явно фиксируем удаление, чтобы изменения не откатывались
    await db_session.commit()

    # Проверяем, что продавец удален
    seller_in_db = await db_session.get(Seller, seller_id)
    assert seller_in_db is None

