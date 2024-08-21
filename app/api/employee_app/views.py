from datetime import datetime, timedelta

from fastapi import APIRouter
from starlette import status
from starlette.exceptions import HTTPException

from app.api.employee_app.data_pydantic import EmployeeItem
from app.api.employee_app.models import Employees
from app.core.config import settings
from app.utils.auth import create_access_token
from app.utils.rsa_tools import decryption_message
from app.utils.totp_tools import create_totp_token

employee_routers = APIRouter()


@employee_routers.post('/login')
async def employee_login(item: EmployeeItem):
    """员工登录"""
    employee = await Employees.filter(phone=item.phone).first()
    if not employee or employee.is_delete:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='员工不存在',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    elif not employee.is_active:
        return {'msg': '员工未激活, 请前往激活'}

    # 验证
    if item.require_pass.upper() != create_totp_token(employee.secret_key):
        return {'msg': '「require_pass」无效或以失效'}

    now = datetime.today()
    employee.last_login = now
    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    access_token = create_access_token(
        data={'ut': 'employee', 'uid': employee.id},
        expires_delta=access_token_expires,
    )

    return {'msg': '登录成功', 'access_token': access_token, 'token_type': 'bearer'}
