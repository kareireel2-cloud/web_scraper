from sqlalchemy import  Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .session import Base


class UrlData(Base):
    __tablename__ = "url_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(300), nullable=False, unique= True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    html_body: Mapped[str] = mapped_column(Text, nullable=False)
