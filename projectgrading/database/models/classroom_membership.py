from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class ClassroomMembership(Base):
    __tablename__ = "classroom_memberships"

    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id"), primary_key=True, index=True, nullable=False
    )
    classroom_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("classrooms.id"), primary_key=True, index=True, nullable=False
    )
