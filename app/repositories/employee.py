from typing import Sequence, Iterable, Optional

from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EmployeeModel, CompanyModel


class EmployeeRepository:
    """Операции с сотрудниками."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ---------- GET ----------
    async def get_by_username(self, username: str) -> Optional[EmployeeModel]:
        stmt = select(EmployeeModel).where(EmployeeModel.username == username)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_id(self, employee_id: int) -> Optional[EmployeeModel]:
        res = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.id == employee_id)
        )
        return res.scalar_one_or_none()

    async def get_by_id_with_companies(
        self,
        employee_id: int,
        filter_active_companies: bool = False,
    ) -> Optional[EmployeeModel]:
        """Загрузить сотрудника + связанные компании.

        filter_active_companies=True  → в options накладываем
        CompanyModel.is_active == True
        """
        opts = selectinload(EmployeeModel.companies)
        if filter_active_companies:
            opts = opts.options(
                selectinload(
                    CompanyModel).where(
                        CompanyModel.is_active.is_(True)
                )
            )

        res = await self.session.execute(
            select(EmployeeModel)
            .options(opts)
            .where(EmployeeModel.id == employee_id)
        )
        return res.scalar_one_or_none()

    # ---------- CREATE ----------
    async def create_employee(
        self,
        *,
        employee: EmployeeModel,
        company_ids: Iterable[int] | None = None,
    ) -> EmployeeModel:
        """Создать сотрудника + связать с компаниями."""
        async with self.session.begin():
            self.session.add(employee)
            if company_ids:
                companies = await self._get_companies(company_ids)
                employee.companies.extend(companies)
        return employee

    # ---------- UPDATE ----------
    async def update_employee(
        self,
        employee_id: int,
        data: dict,
        company_ids: Iterable[int] | None = None,
    ) -> Optional[EmployeeModel]:
        """
        Обновить поля и, если передан company_ids, пересоздать M-N связи:
        старые удаляются, новые добавляются.
        """
        async with self.session.begin():
            emp = await self.get_by_id(employee_id)
            if not emp:
                return None

            for key, value in data.items():
                setattr(emp, key, value)

            if company_ids is not None:
                emp.companies = await self._get_companies(company_ids)
        return emp

    # ---------- DELETE ----------
    async def delete_employee(self, employee_id: int) -> bool:
        """Удалить сотрудника и порвать связи."""
        async with self.session.begin():
            emp = await self.get_by_id(employee_id)
            if not emp:
                return False
            emp.companies.clear()        # разрыв M-N
            await self.session.delete(emp)
        return True

    # ---------- DEACTIVATE ----------
    async def disactivate_by_id(self, employee_id: int) -> bool:
        async with self.session.begin():
            res = await self.session.execute(
                update(EmployeeModel)
                .where(EmployeeModel.id == employee_id)
                .values(is_active=False)
                .returning(EmployeeModel.id)
            )
            return res.scalar_one_or_none() is not None

    # ---------- HELPERS ----------
    async def _get_companies(self, ids: Iterable[int]) -> Sequence[CompanyModel]:
        res = await self.session.execute(
            select(CompanyModel).where(CompanyModel.id.in_(list(ids)))
        )
        return res.scalars().all()
