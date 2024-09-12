from datetime import datetime

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class AccessLoggerMiddleware(BaseHTTPMiddleware):
    """
    记录请求日志
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = datetime.now()
        response = await call_next(request)
        end_time = datetime.now()
        client = request.client
        host = client.host if client else None
        logger.info(f'{response.status_code} {host} {request.method} {request.url} {end_time - start_time}')
        return response
