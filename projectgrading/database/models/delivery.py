from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, LargeBinary
from sqlalchemy import text as sql_text
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, ForeignKey("teams.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=sql_text("CURRENT_TIMESTAMP"), index=True
    )
    file: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
