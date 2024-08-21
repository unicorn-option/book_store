from pydantic import BaseModel


class BaseEmployeeItem(BaseModel):
    phone: str
    gender: str = 'male'


class EmployeeItem(BaseEmployeeItem):
    require_pass: str
