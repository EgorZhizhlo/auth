from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class _CompanyBase(BaseModel):
    name: str = Field(max_length=200)
    inn: str = Field(max_length=12, pattern=r"^\d{10,12}$")


class CompanyCreate(_CompanyBase):
    """Входные данные для создания компании."""
    pass


class CompanyUpdate(BaseModel):
    """Патч-обновление компании; все поля опциональны."""
    name: str | None = Field(None, max_length=200)
    inn: str | None = Field(None, max_length=12, pattern=r"^\d{10,12}$")
    is_active: bool | None = None


class CompanyOut(_CompanyBase):
    """Ответ API."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
