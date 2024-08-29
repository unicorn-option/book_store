import json
from urllib.parse import parse_qs

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.app.utils.signature import verify_signature


class SignatureMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, paths_to_verify: set):
        super(SignatureMiddleware, self).__init__(app)
        self.paths_to_verify = paths_to_verify

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.paths_to_verify:
            query_params = parse_qs(str(request.query_params))
            query_params = {k: ','.join(v) for k, v in query_params.items()}
            body_bytes = await request.body()
            body = json.loads(body_bytes)

            async def receive() -> dict:
                return {'type': 'http.request', 'body': body_bytes}

            request._receive = receive

            params = {**query_params, **body}

            signature = request.headers.get('sign', '')
            if not signature:
                return JSONResponse(status_code=400, content={'msg': '缺少必要请求头参数: sign'})

            if not verify_signature(params, signature):
                return JSONResponse(status_code=400, content={'msg': '请求参数不合法'})

        response = await call_next(request)

        return response
