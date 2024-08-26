from typing import List

from pydantic import BaseModel

from src.app.api.employee_app.data_pydantic import BaseEmployeeItem


class AdministratorItem(BaseModel):
    phone: str
    password: str


class EmployeesItem(BaseModel):
    employee_data: List[BaseEmployeeItem]
