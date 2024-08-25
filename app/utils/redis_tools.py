import json

from aioredis import create_redis_pool


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
        if not self.redis_db_dict.get(db_name):
            self.redis_db_dict[db_name] = await create_redis_pool(**redis_config)

    async def close_redis_pool(self, db_name):
        self.redis_db_dict[db_name].close()
        await self.redis_db_dict[db_name].wait_closed()

    async def close_all_redis_pool(self):
        for db_name, redis_pool in self.redis_db_dict.items():
            redis_pool.close()
            await redis_pool.wait_closed()

    async def store_routes_as_hashes(self, db_name, route_data):
        redis_client = self.redis_db_dict[db_name]
        # 1️⃣ 直接用 HSET 命令
        # for path, data in route_data.items():
        #     await redis_client.hset('book_store_routes', path, json.dumps(data))
        # 2️⃣ 直接使用 HMSET 命令
        # for path, data in route_data.items():
        #     await redis_client.hmset('book_store_routes', path, json.dumps(data))
        # 2️⃣ 通过 hmset_dict 方法间接使用 HMSET 命令
        await redis_client.hmset_dict(
            'book_store_routes',
            {path: json.dumps(data) for path, data in route_data.items()})

    async def get_all_routes_by_hashes(self, db_name):
        redis_client = self.redis_db_dict[db_name]
        routes = await redis_client.hgetall('book_store_routes')
        return {name.decode('utf-8'): json.loads(data.decode('utf-8')) for name, data in routes.items()}
