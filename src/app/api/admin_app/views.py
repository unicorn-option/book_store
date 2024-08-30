from datetime import datetime, timedelta

from fastapi import APIRouter
from starlette import status
from starlette.exceptions import HTTPException
from tortoise.exceptions import IntegrityError
from tortoise.transactions import in_transaction

from src.app.api.admin_app.data_pydantic import AdministratorItem, EmployeesItem
from src.app.api.admin_app.models import Administrator
from src.app.api.employee_app.models import Employees
from src.app.core.config import settings
from src.app.utils.auth import create_access_token
from src.app.utils.totp_tools import generate_secret_key

admin_routers = APIRouter()


@admin_routers.post('/register')
async def admin_register(item: AdministratorItem):
    """管理员注册"""
    # 检查是否已经存在管理员
    if await Administrator.filter(is_delete=False).exists():
        raise HTTPException(status_code=400, detail='管理员账号已存在, 无需再次注册')

    # 不存在, 创建新管理员
    try:
        async with in_transaction():
            admin = Administrator(
                phone=item.phone,
                password=item.password,
                is_active=True,
            )
            await admin.save()

        return {'msg': '创建管理员成功'}
    except IntegrityError:
        raise HTTPException(status_code=500, detail='创建管理员失败')


@admin_routers.post('/login')
async def admin_login(item: AdministratorItem):
    """管理员登录"""
    admin = await Administrator.filter(phone=item.phone).first()
    if not admin or admin.is_delete:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='管理员不存在',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    if admin.password == item.password:
        admin.last_login = datetime.today()
        access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        access_token = create_access_token(
            data={'ut': 'admin', 'uid': admin.id},
            expires_delta=access_token_expires,
        )

        return {'msg': '登录成功', 'access_token': access_token, 'token_type': 'bearer'}
    else:
        return {'msg': '密码错误'}


@admin_routers.post('/employees')
async def create_employee_account(items: EmployeesItem):
    results = {}
    for item in items.employee_data:
        employee = await Employees.filter(phone=item.phone).first()
        if employee:
            code = 2
            msg = f'员工账号「{employee.phone}」已分配'
        else:
            code = 1
            msg = '分配成功'
            # 获取私钥和公钥
            secret_key = generate_secret_key()
            employee = await Employees.create(
                phone=item.phone,
                secret_key=secret_key,
                gender=item.gender
            )

            await employee.save()

        results[employee.phone] = {
            'code': code,
            'uid': employee.id,
            'secret_key': employee.secret_key,
            'msg': msg,
        }

    return {'data': results}
