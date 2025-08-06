from sqlalchemy import Column, DateTime, Boolean, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.time_utils import utc_now
from app.infrastructure.db.base import Base


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(36), unique=True, nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey(
        "employees.id"), nullable=False, index=True)

    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, default=utc_now)

    employee = relationship("EmployeeModel", back_populates="refresh_tokens")
