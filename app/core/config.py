import asyncio
import os

from tortoise import Tortoise

RUN_ENV = os.environ.get('RUN_ENV', 'PROD')
OS_USER = os.environ.get('USER', 'root')


class Settings:
    FastAPI_SETTINGS = {
        "title": "生产",
        "description": "描述",
        "version": "0.0.1",
    }
    sem = asyncio.Semaphore(30)         # 控制项目中 异步请求其他网址时的并发量
    retry = 30                          # 网络重访次数

    # 数据库 配置
    # DB = {
    #     "host": os.environ.get('DB_HOST', '127.0.0.1'),
    #     "port": os.environ.get('DB_PORT', 5432),
    #     "user": os.environ.get('DB_USER', 'postgres'),
    #     "password": os.environ.get('DB_PASSWORD', 'unicorn'),
    #     "database": 'postgres',
    #     "charset": "utf8mb4",
    # }
    # db_url: str = ('postgres://{user}.{password}@{host}:{port}/{database}?charset={charset}'
    #                .format_map(DB))

    DATABASES = {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": os.environ.get('PG_HOST', '127.0.0.1'),
                "port": os.environ.get('PG_PORT', 5432),
                "user": os.environ.get('PG_USER', 'postgres'),
                "password": os.environ.get('PG_PASSWORD', 'unicorn'),
                "database": os.environ.get('PG_DB', 'postgres'),
                # "charset": "utf8mb4",
            }
        }
    }

    TORTOISE_ORM = {
        "connections": DATABASES,
        "apps": {
            "models": {
                "models": [
                    # 'app.models',
                    'app.api.reader_app.models',
                    'app.api.employee_app.models',
                    'app.api.admin_app.models',
                    'app.api.access_app.models',
                    'aerich.models',
                ],
                "default_connection": "default",
            }
        }
    }

    CORS = {
        "allow_origins": ['*'],             # 设置允许的 origins 来源
        "allow_credentials": True,
        "allow_methods": ['*'],             # 设置允许跨域的 HTTP 方法
        "allow_headers": ['*'],             # 允许跨域的 headers, 可以用来鉴别来源等作用
    }
    PATHS_TO_VERIFY = {
        '/reader/register',
        '/reader/login',
        '/admin/register',
        '/admin/login',
        '/employee/login',
    }
    TOKEN_EXCLUDE_PATHS = {
        '/reader/register',
        '/reader/login',
        '/admin/register',
        '/admin/login',
        '/employee/login',
    }

    # 程序配置
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = os.path.join(BASE_DIR, 'logs')           # 日志目录
    if not os.path.exists(log_path):
        os.mkdir(log_path)

    # 保存文件路径配置
    if OS_USER == 'root':
        BASE_PATH = '/root/book_store'
    else:
        BASE_PATH = f'/Users/{OS_USER}/book_store'
    if not os.path.exists(BASE_PATH):
        os.mkdir(BASE_PATH)

    BASE_DOMAIN = 'https://exam-domain.com'

    # 签名和 token 加密 Key
    SECRET_KEY = 'JwX4jK9cA7qVbF8PzL2rN1yXt5EgZd!7'
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 6
    # RSA 密钥长度
    RSA_KEY_SIZE = 2048


class DevSettings(Settings):
    FastAPI_SETTINGS = {
        "title": "开发测试",
        "description": "描述",
        "version": "0.0.1",
    }
    # 本地开发数据库 配置
    # DB = {
    #     "host": '127.0.0.1',
    #     "port": 5432,
    #     "user": 'postgres',
    #     "password": 'unicorn',
    #     "database": 'postgres',
    #     'charset': 'utf8mb4',
    # }

    DATABASES = {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": '127.0.0.1',
                "port": 5432,
                "user": 'postgres',
                "password": 'unicorn',
                "database": 'postgres',
                'charset': 'utf8mb4',
            }
        }
    }

    # 保存文件路径配置
    BASE_PATH = '/Users/ming/book_store'

    # 外部访问服务器的主域名
    BASE_DOMAIN = 'http://127.0.0.1:8000'
    # RSA 密钥长度
    RSA_KEY_SIZE = 1024


if RUN_ENV == 'PROD':
    settings = Settings
else:
    settings = DevSettings


TORTOISE_ORM = settings.TORTOISE_ORM


async def init():
    try:
        await Tortoise.init(config=settings.TORTOISE_ORM)
        await Tortoise.generate_schemas()
    except ConnectionRefusedError as e:
        print(e)


async def do_stuff():
    await Tortoise.close_connections()
