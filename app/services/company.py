from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from models.company import CompanyModel
from repositories.company import CompanyRepository
from schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
    """Бизнес-логика вокруг компаний."""

    def __init__(self, db: AsyncSession) -> None:
        self._repo = CompanyRepository(db)

    # ---------- READ ----------
    async def get_by_id(self, company_id: int) -> Optional[CompanyModel]:
        return await self._repo.get_by_id(company_id)

    # ---------- CREATE ----------
    async def create_company(self, data: CompanyCreate) -> CompanyModel:
        company = CompanyModel(
            name=data.name,
            inn=data.inn,
        )
        return await self._repo.create(company)

    # ---------- UPDATE ----------
    async def update_company(
        self,
        company_id: int,
        data: CompanyUpdate,
    ) -> Optional[CompanyModel]:
        payload = data.model_dump(exclude_unset=True, exclude_none=True)
        return await self._repo.update(company_id, payload)

    # ---------- DELETE / DEACTIVATE ----------
    async def delete_company(self, company_id: int) -> bool:
        return await self._repo.delete(company_id)

    async def disactivate_company(self, company_id: int) -> bool:
        return await self._repo.disactivate_by_id(company_id)
