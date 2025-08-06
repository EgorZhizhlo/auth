from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CompanyModel


class CompanyRepository:
    """Операции с компаниями."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ---------- GET ----------
    async def get_by_id(self, company_id: int) -> Optional[CompanyModel]:
        res = await self.session.execute(
            select(CompanyModel).where(CompanyModel.id == company_id)
        )
        return res.scalar_one_or_none()

    # ---------- CREATE ----------
    async def create(self, company: CompanyModel) -> CompanyModel:
        async with self.session.begin():
            self.session.add(company)
        return company

    # ---------- UPDATE ----------
    async def update(self, company_id: int, data: dict) -> Optional[CompanyModel]:
        async with self.session.begin():
            comp = await self.get_by_id(company_id)
            if not comp:
                return None
            for k, v in data.items():
                setattr(comp, k, v)
        return comp

    # ---------- DELETE ----------
    async def delete(self, company_id: int) -> bool:
        async with self.session.begin():
            comp = await self.get_by_id(company_id)
            if not comp:
                return False
            comp.employees.clear()      # разрыв M-N
            await self.session.delete(comp)
        return True

    # ---------- DEACTIVATE ----------
    async def disactivate_by_id(self, company_id: int) -> bool:
        async with self.session.begin():
            res = await self.session.execute(
                update(CompanyModel)
                .where(CompanyModel.id == company_id)
                .values(is_active=False)
                .returning(CompanyModel.id)
            )
            return res.scalar_one_or_none() is not None
