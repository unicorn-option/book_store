from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.admin_app.views import admin_routers
from app.api.employee_app.views import employee_routers
from app.api.reader_app.views import reader_routers
from app.core.config import init, do_stuff, settings
from app.utils.middlewares.jwt_middleware import JWTMiddleware
from app.utils.middlewares.signature_middleware import SignatureMiddleware

app = FastAPI()

# 注册中间件
app.add_middleware(
    CORSMiddleware,
    **settings.CORS
)
app.add_middleware(
    SignatureMiddleware,
    paths_to_verify=settings.PATHS_TO_VERIFY,
)
app.add_middleware(
    JWTMiddleware,
    exclude_paths=settings.TOKEN_EXCLUDE_PATHS,
)

# 注册子应用路由
app.include_router(router=reader_routers, prefix='/reader')
app.include_router(router=admin_routers, prefix='/admin')
app.include_router(router=employee_routers, prefix='/employee')


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.on_event('startup')
async def startup_event():
    """添加在应用程序启动之前运行初始化数据库"""
    await init()


@app.on_event('shutdown')
async def shutdown_event():
    """添加在应用程序关闭是关闭所有数据库连接"""
    await do_stuff()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app='main:app',
        host='0.0.0.0',
        port=8001,
        reload=True,
    )
