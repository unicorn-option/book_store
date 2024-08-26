import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.app.core.config import settings
from src.app.utils.auth import USER_MODEL


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_paths):
        super(JWTMiddleware, self).__init__(app)
        self.exclude_paths = exclude_paths

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        authorization: str = request.headers.get('Authorization')
        if not authorization:
            return JSONResponse(
                status_code=403,
                content={'msg': '没有身份标识'})

        token = authorization.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
            user_type: str = payload.get('ut')
            uid: int = payload.get('uid')
            if not user_type or user_type not in USER_MODEL or not uid:
                return JSONResponse(
                    status_code=403,
                    content={'msg': '错误身份标识'})

            user = await USER_MODEL[user_type].get(id=uid)
            if not user:
                return JSONResponse(
                    status_code=403,
                    content={'msg': '无效身份标识'})

            request.state.user = user
        except Exception:
            return JSONResponse(
                status_code=403,
                content={'msg': '认证失败'})

        response = await call_next(request)

        return response
