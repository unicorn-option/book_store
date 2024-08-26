from fastapi import FastAPI, routing
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from tortoise import Tortoise

from src.app.api.admin_app.views import admin_routers
from src.app.api.employee_app.views import employee_routers
from src.app.api.reader_app.views import reader_routers
from src.app.core.config import init_db, do_stuff, settings
from src.app.utils.middlewares.jwt_middleware import JWTMiddleware
from src.app.utils.middlewares.signature_middleware import SignatureMiddleware
from src.app.utils.redis_tools import DatabasePool

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


@app.get("/", description='根地址')
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}", tags=['hello', 'demo', 'api', 'main'])
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.on_event('startup')
async def startup_event():
    """添加在应用程序启动之前运行初始化数据库"""
    await init_db()

    database_pool = DatabasePool()
    await database_pool.create_redis_pool(settings.REDIS_CONFIG)
    app.state.database_pool = database_pool


@app.on_event('startup')
async def check_unsaved_routes():
    routes_info_name = {}
    for route in app.routes:
        if isinstance(route, routing.APIRoute):
            methods = '&'.join(sorted(list(route.methods)))
            tags = '^'.join(sorted(route.tags))
            data = {
                'path': route.path,
                'name': route.name,
                'methods': methods,
                'tags': tags,
                'description': route.description,
            }
            routes_info_name[route.name] = data

    route_list = await app.state.database_pool.get_all_routes_by_hashes(settings.REDIS_CONFIG['db_name'])

    update_values, update_paths = [], []
    for name, data in routes_info_name.items():
        if name in route_list and data['path'] != route_list[name]['path']:
            update_values.append("when '{0}' then '{1}'".format(route_list[name]['path'], data['path']))
            update_paths.append(route_list[name]['path'])

    if update_values:
        sql = (
            'UPDATE permission SET api_path=CASE api_path {0} END WHERE api_path in ($1);'
            .format(' '.join(update_values)))
        await Tortoise.get_connection('default').execute_query(query=sql, values=update_paths)

    await app.state.database_pool.store_routes_as_hashes(
        settings.REDIS_CONFIG['db_name'],
        routes_info_name,
    )


@app.on_event('shutdown')
async def shutdown_event():
    """添加在应用程序关闭是关闭所有数据库连接"""
    await do_stuff()
    # 关闭 book_store 这一个连接
    # await app.state.database_pool.close_redis_pool('book_store')
    # 关闭所有连接
    await app.state.database_pool.close_all_redis_pool()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app='main:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
    )
