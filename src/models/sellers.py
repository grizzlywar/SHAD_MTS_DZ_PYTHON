from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel
# Убираем прямой импорт Book, используем строку в relationship

class Seller(BaseModel):
    __tablename__ = "sellers_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    e_mail: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)

    # Связь "один ко многим": один Seller -> много Book
    books: Mapped[list["Book"]] = relationship(
        "Book",  # вместо импорта используем строку
        back_populates="seller",
        cascade="all, delete-orphan",
    )
