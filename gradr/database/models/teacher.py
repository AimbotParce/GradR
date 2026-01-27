from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    classroom_id: Mapped[int] = mapped_column(Integer, ForeignKey("classrooms.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
