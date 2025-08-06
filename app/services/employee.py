from typing import Iterable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.security import get_password_hash           # 🔑 хешируем пароли
from models.employee import EmployeeModel
from repositories.employee import EmployeeRepository
from schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    """Бизнес-логика вокруг сотрудников."""

    def __init__(self, db: AsyncSession) -> None:
        self._repo = EmployeeRepository(db)

    # ---------- READ ----------
    async def get_by_username(self, username: str) -> Optional[EmployeeModel]:
        return await self._repo.get_by_username(username)

    async def get_by_id(self, employee_id: int) -> Optional[EmployeeModel]:
        return await self._repo.get_by_id(employee_id)

    async def get_by_id_with_companies(
        self,
        employee_id: int,
        only_active_companies: bool = False,
    ) -> Optional[EmployeeModel]:
        return await self._repo.get_by_id_with_companies(
            employee_id,
            filter_active_companies=only_active_companies,
        )

    # ---------- CREATE ----------
    async def create_employee(self, data: EmployeeCreate) -> EmployeeModel:
        hashed_pwd = get_password_hash(data.password)
        employee = EmployeeModel(
            username=data.username,
            password=hashed_pwd,
            last_name=data.last_name,
            name=data.name,
            patronymic=data.patronymic,
            status=data.status,
        )
        return await self._repo.create(
            employee=employee,
            company_ids=data.company_ids,
        )

    # ---------- UPDATE ----------
    async def update_employee(
        self,
        employee_id: int,
        data: EmployeeUpdate,
    ) -> Optional[EmployeeModel]:
        payload = data.model_dump(exclude_unset=True, exclude_none=True)
        company_ids: Optional[Iterable[int]] = payload.pop("company_ids", None)

        # если передали новый пароль ― хешируем
        if "password" in payload:
            payload["password"] = get_password_hash(payload["password"])

        return await self._repo.update(
            employee_id=employee_id,
            data=payload,
            company_ids=company_ids,
        )

    # ---------- DELETE / DEACTIVATE ----------
    async def delete_employee(self, employee_id: int) -> bool:
        return await self._repo.delete(employee_id)

    async def disactivate_employee(self, employee_id: int) -> bool:
        return await self._repo.disactivate_by_id(employee_id)
