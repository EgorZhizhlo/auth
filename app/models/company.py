from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from infrastructure.db.base import Base
from core.time_utils import utc_now
from .employees_companies import employees_companies


class CompanyModel(Base):
    __tablename__ = 'companies'

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

    name = Column(String(200), unique=True, nullable=False)
    inn = Column(String(12), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    employees = relationship(
        'EmployeeModel',
        secondary=employees_companies,
        back_populates='companies',
        lazy='selectin'
    )
