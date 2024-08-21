from datetime import datetime, timedelta

import jwt

from app.api.admin_app.models import Administrator
from app.api.employee_app.models import Employees
from app.api.reader_app.models import Readers
from app.core.config import settings

USER_MODEL = {
    'reader': Readers,
    'employee': Employees,
    'admin': Administrator,
}


def create_access_token(data: dict, expires_delta):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.today() + expires_delta
    else:
        expire = datetime.now() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)

    to_encode['exp'] = expire
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt
