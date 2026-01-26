from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class TeamMembership(Base):
    __tablename__ = "team_memberships"

    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), primary_key=True, index=True)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), primary_key=True, index=True)
