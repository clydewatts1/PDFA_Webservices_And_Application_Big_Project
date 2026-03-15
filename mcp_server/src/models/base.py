from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


HIGH_DATE = datetime(9999, 1, 1, 0, 0, 0)


def utcnow_naive() -> datetime:
	return datetime.now(UTC).replace(tzinfo=None)


class Base(DeclarativeBase):
	pass


class ControlColumnsMixin:
	EffFromDateTime: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
	EffToDateTime: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
	DeleteInd: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	InsertUserName: Mapped[str] = mapped_column(String(128), nullable=False)
	UpdateUserName: Mapped[str] = mapped_column(String(128), nullable=False)

	@staticmethod
	def control_defaults(actor: str, effective_from: datetime | None = None) -> dict[str, object]:
		now = effective_from or utcnow_naive()
		return {
			"EffFromDateTime": now,
			"EffToDateTime": HIGH_DATE,
			"DeleteInd": 0,
			"InsertUserName": actor,
			"UpdateUserName": actor,
		}
