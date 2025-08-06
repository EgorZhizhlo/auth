from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict

from .company import CompanyOut


class _EmployeeBase(BaseModel):
    username: str = Field(max_length=150)
    last_name: str = Field(max_length=100)
    name: str = Field(max_length=100)
    patronymic: str = Field(max_length=100)
    # enum-значения задашь валидацией, если нужно
    status: str = Field(max_length=30)


# ---------- CREATE ----------
class EmployeeCreate(_EmployeeBase):
    password: str = Field(min_length=6)
    company_ids: List[int] | None = None      # связь Many-to-Many


# ---------- UPDATE ----------
class EmployeeUpdate(BaseModel):
    """PATCH-обновление; все поля опциональны."""
    password: str | None = Field(None, min_length=6)
    last_name: str | None = Field(None, max_length=100)
    name: str | None = Field(None, max_length=100)
    patronymic: str | None = Field(None, max_length=100)
    status: str | None = Field(None, max_length=30)
    is_active: bool | None = None
    company_ids: List[int] | None = None


# ---------- OUT ----------
class EmployeeOut(_EmployeeBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeOutWithCompanies(EmployeeOut):
    companies: List[CompanyOut]

    model_config = ConfigDict(from_attributes=True)
