import os
from typing import Optional


class RedisConfig:
    """redis 配置类，从环境变量中读取配置"""

    def __init__(self):
        self.host: str = os.getenv("REDIS_HOST", "localhost")
        self.port: int = int(os.getenv("REDIS_PORT", "6379"))
        self.db: int = int(os.getenv("REDIS_DB", "0"))
        self.password: Optional[str] = os.getenv("REDIS_PASSWORD", None)


redis_config = RedisConfig()
