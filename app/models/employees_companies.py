from sqlalchemy import Table, Column, Integer, ForeignKey
from infrastructure.db.base import Base

employees_companies = Table(
    'employees_companies',
    Base.metadata,
    Column('employee_id', Integer, ForeignKey(
        'employees.id'), primary_key=True),
    Column('company_id', Integer, ForeignKey(
        'companies.id'), primary_key=True),
)
