import json

from aioredis import ConnectionPool, Redis


class DatabasePool:

    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'redis_db_dict'):
            self.redis_db_dict = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(DatabasePool, cls).__new__(cls)

        return cls._instance

    async def create_redis_pool(self, redis_config):
        redis_config = redis_config.copy()
        db_name = redis_config.pop('db_name', 'book_store')

        # 创建连接池
        if not self.redis_db_dict.get(db_name):
            pool = ConnectionPool(**redis_config)
            self.redis_db_dict[db_name] = await Redis(connection_pool=pool)

    async def close_redis_pool(self, db_name):
        redis_pool = self.redis_db_dict.get(db_name)
        if redis_pool:
            await redis_pool.close()
    async def close_all_redis_pool(self):
        for db_name, redis_pool in self.redis_db_dict.items():
            await redis_pool.close()

    async def store_routes_as_hashes(self, db_name, route_data):
        redis_client = self.redis_db_dict[db_name]
        # 1️⃣ 直接用 HSET 命令
        # for path, data in route_data.items():
        #     await redis_client.hset('book_store_routes', path, json.dumps(data))
        # 2️⃣ 直接使用 HMSET 命令
        # for path, data in route_data.items():
        #     await redis_client.hmset('book_store_routes', path, json.dumps(data))
        # 2️⃣ 通过 hmset_dict 方法间接使用 HMSET 命令
        await redis_client.hset(
            'book_store_routes',
            mapping={path: json.dumps(data) for path, data in route_data.items()})

    async def get_all_routes_by_hashes(self, db_name):
        redis_client = self.redis_db_dict[db_name]
        routes = await redis_client.hgetall('book_store_routes')
        return {name: json.loads(data) for name, data in routes.items()}
