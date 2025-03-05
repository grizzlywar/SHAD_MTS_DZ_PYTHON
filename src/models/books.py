from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from .sellers import Seller  # Здесь импортируем Seller, так как это не вызывает циклического импорта

class Book(BaseModel):
    __tablename__ = "books_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int]
    pages: Mapped[int]

    # Поле seller_id с внешним ключом на таблицу sellers_table
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("sellers_table.id"),
        nullable=False
    )

    # Связь "многие к одному": одна книга принадлежит одному продавцу
    seller: Mapped["Seller"] = relationship(
        "Seller",
        back_populates="books",
    )
