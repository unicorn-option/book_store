from datetime import datetime, timedelta

from fastapi import APIRouter
from starlette import status
from starlette.exceptions import HTTPException

from src.app.api.reader_app.data_pydantic import ReaderItem
from src.app.api.reader_app.models import Readers
from src.app.core.config import settings
from src.app.utils.auth import create_access_token

reader_routers = APIRouter()


@reader_routers.post('/register')
async def reader_register(item: ReaderItem):
    """读者注册"""
    reader = await Readers.filter(phone=item.phone)
    if reader:
        return {'msg': '已存在'}

    reader = await Readers(
        phone=item.phone,
        nick_name=item.nick_name if item.nick_name else f'读者_{item.phone}',
        password=item.password,
        age=item.age,
        gender=item.gender,
        avatar=item.avatar,
    )

    await reader.save()

    return {'msg': '注册成功'}


@reader_routers.post('/login')
async def reader_login(item: ReaderItem):
    """读者登录"""
    reader = await Readers.filter(phone=item.phone).first()
    if not reader or reader.is_delete:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='用户不存在',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    elif not reader.is_active:
        return {'msg': '用户未激活, 请前往激活'}

    if reader.password == item.password:
        reader.last_login = datetime.today()
        access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        access_token = create_access_token(
            data={'ut': 'reader', 'uid': reader.id},
            expires_delta=access_token_expires,
        )

        return {'msg': '登录成功', 'access_token': access_token, 'token_type': 'bearer'}
    else:
        return {'msg': '密码错误'}
