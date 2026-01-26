from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Grade(Base):
    __tablename__ = "grades"

    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), primary_key=True, nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), primary_key=True, nullable=False)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey("teachers.id"), primary_key=True, nullable=False)
    grade: Mapped[float] = mapped_column(Float, CheckConstraint("grade >= 0.0 AND grade <= 10.0"), nullable=False)
