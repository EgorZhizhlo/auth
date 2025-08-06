from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from infrastructure.db.base import Base
from core.time_utils import utc_now
from .employees_companies import employees_companies


class EmployeeModel(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now
    )
    last_login = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now
    )

    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    last_name = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    patronymic = Column(String(100), nullable=False)
    status = Column(String(30), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    companies = relationship(
        'CompanyModel',
        secondary=employees_companies,
        back_populates='employees',
        lazy='selectin'
    )

    refresh_tokens = relationship(
        "RefreshTokenModel",
        back_populates="employee",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
