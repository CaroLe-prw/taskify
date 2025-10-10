from typing import Any, Optional, Union, List
import redis
import json
import time
import uuid

from . import redis_config


class RedisHelper:

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        password: Optional[str] = None,
    ):
        """
        初始化 RedisHelper 类，设置 Redis 连接信息
        如果不传参数，则使用环境变量配置
        :param host: Redis 服务器主机，默认从环境变量 REDIS_HOST 读取
        :param port: Redis 服务器端口，默认从环境变量 REDIS_PORT 读取
        :param db: Redis 数据库，默认从环境变量 REDIS_DB 读取
        :param password: Redis 密码，默认从环境变量 REDIS_PASSWORD 读取
        """
        self.redis_client = redis.StrictRedis(
            host=host or redis_config.host,
            port=port or redis_config.port,
            db=db or redis_config.db,
            password=password or redis_config.password,
            decode_responses=True,
        )

    # ==================== String（字符串）操作 ====================

    def set(
        self,
        key: str,
        value: Union[str, int, float, dict, list],
        ex: Optional[int] = None,
        serialize: bool = True,
    ) -> bool:
        """
        设置键值对，自动支持 JSON 序列化
        :param key: 键
        :param value: 值，可以是字符串、整数、浮点数、字典或列表
        :param ex: 过期时间（秒），默认不设置过期时间
        :param serialize: 是否自动序列化 dict/list 为 JSON，默认 True
        :return: 是否成功
        """
        try:
            # 如果是字典或列表且启用序列化，则自动转为 JSON
            if serialize and isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)

            if ex:
                self.redis_client.setex(key, ex, value)
            else:
                self.redis_client.set(key, value)
            return True
        except Exception as e:
            print(f"Error setting key {key}: {e}")
            return False

    def get(self, key: str, deserialize: bool = True) -> Optional[Any]:
        """
        获取指定键的值，自动支持 JSON 反序列化
        :param key: 键
        :param deserialize: 是否尝试自动反序列化 JSON，默认 True
        :return: 键对应的值，如果键不存在，则返回 None
        """
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None

            # 如果启用反序列化，尝试将 JSON 字符串转为对象
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # 不是 JSON 格式，返回原始字符串
                    return value
            return value
        except Exception as e:
            print(f"Error getting key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """
        删除指定键
        :param key: 键
        :return: 是否成功
        """
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        检查指定的键是否存在
        :param key: 键
        :return: 键是否存在
        """
        try:
            return self.redis_client.exists(key)
        except Exception as e:
            print(f"Error checking existence of key {key}: {e}")
            return False

    def set_multiple(self, mapping: dict, ex: Optional[int] = None) -> bool:
        """
        批量设置多个键值对
        :param mapping: 键值对字典
        :param ex: 过期时间（秒），可选
        :return: 是否成功
        """
        try:
            if ex:
                for key, value in mapping.items():
                    self.redis_client.setex(key, ex, value)
            else:
                self.redis_client.mset(mapping)
            return True
        except Exception as e:
            print(f"Error setting multiple keys: {e}")
            return False

    def get_multiple(self, keys: list) -> dict:
        """
        批量获取多个键的值
        :param keys: 键列表
        :return: 键值对字典
        """
        try:
            values = self.redis_client.mget(keys)
            return dict(zip(keys, values))
        except Exception as e:
            print(f"Error getting multiple keys: {e}")
            return {}

    def increment(self, key: str, amount: int = 1) -> Union[int, None]:
        """
        对指定键的值进行自增
        :param key: 键
        :param amount: 增量，默认为 1
        :return: 增加后的值，如果操作失败，则返回 None
        """
        try:
            return self.redis_client.incrby(key, amount)
        except Exception as e:
            print(f"Error incrementing key {key}: {e}")
            return None

    def decrement(self, key: str, amount: int = 1) -> Union[int, None]:
        """
        对指定键的值进行自减
        :param key: 键
        :param amount: 减量，默认为 1
        :return: 减少后的值，如果操作失败，则返回 None
        """
        try:
            return self.redis_client.decrby(key, amount)
        except Exception as e:
            print(f"Error decrementing key {key}: {e}")
            return None

    def hset(self, hash_name: str, key: str, value: Any) -> bool:
        """
        向哈希表中设置字段值
        :param hash_name: 哈希表名称
        :param key: 字段名
        :param value: 字段值
        :return: 是否成功
        """
        try:
            self.redis_client.hset(hash_name, key, value)
            return True
        except Exception as e:
            print(f"Error setting hash {hash_name}:{key}: {e}")
            return False

    def hget(self, hash_name: str, key: str) -> Optional[Any]:
        """
        获取哈希表中的字段值
        :param hash_name: 哈希表名称
        :param key: 字段名
        :return: 字段值，如果字段不存在，则返回 None
        """
        try:
            return self.redis_client.hget(hash_name, key)
        except Exception as e:
            print(f"Error getting hash {hash_name}:{key}: {e}")
            return None

    def hgetall(self, hash_name: str) -> dict:
        """
        获取哈希表中的所有字段和值
        :param hash_name: 哈希表名称
        :return: 键值对字典
        """
        try:
            return self.redis_client.hgetall(hash_name)
        except Exception as e:
            print(f"Error getting all hash fields for {hash_name}: {e}")
            return {}

    def hmset(self, hash_name: str, mapping: dict) -> bool:
        """
        批量设置哈希表字段
        :param hash_name: 哈希表名称
        :param mapping: 字段值字典
        :return: 是否成功
        """
        try:
            self.redis_client.hset(hash_name, mapping=mapping)
            return True
        except Exception as e:
            print(f"Error setting multiple hash fields for {hash_name}: {e}")
            return False

    def hmget(self, hash_name: str, keys: List[str]) -> List[Optional[str]]:
        """
        批量获取哈希表字段值
        :param hash_name: 哈希表名称
        :param keys: 字段名列表
        :return: 字段值列表
        """
        try:
            return self.redis_client.hmget(hash_name, keys)
        except Exception as e:
            print(f"Error getting multiple hash fields for {hash_name}: {e}")
            return []

    def hdel(self, hash_name: str, *keys: str) -> bool:
        """
        删除哈希表字段
        :param hash_name: 哈希表名称
        :param keys: 要删除的字段名
        :return: 是否成功
        """
        try:
            self.redis_client.hdel(hash_name, *keys)
            return True
        except Exception as e:
            print(f"Error deleting hash fields for {hash_name}: {e}")
            return False

    def hexists(self, hash_name: str, key: str) -> bool:
        """
        判断哈希表字段是否存在
        :param hash_name: 哈希表名称
        :param key: 字段名
        :return: 字段是否存在
        """
        try:
            return self.redis_client.hexists(hash_name, key)
        except Exception as e:
            print(f"Error checking hash field existence for {hash_name}:{key}: {e}")
            return False

    def hlen(self, hash_name: str) -> int:
        """
        获取哈希表字段数量
        :param hash_name: 哈希表名称
        :return: 字段数量
        """
        try:
            return self.redis_client.hlen(hash_name)
        except Exception as e:
            print(f"Error getting hash length for {hash_name}: {e}")
            return 0

    def hincrby(self, hash_name: str, key: str, amount: int = 1) -> Optional[int]:
        """
        哈希表字段值自增
        :param hash_name: 哈希表名称
        :param key: 字段名
        :param amount: 增量，默认为 1
        :return: 增加后的值
        """
        try:
            return self.redis_client.hincrby(hash_name, key, amount)
        except Exception as e:
            print(f"Error incrementing hash field {hash_name}:{key}: {e}")
            return None

    def hkeys(self, hash_name: str) -> List[str]:
        """
        获取哈希表所有字段名
        :param hash_name: 哈希表名称
        :return: 字段名列表
        """
        try:
            return self.redis_client.hkeys(hash_name)
        except Exception as e:
            print(f"Error getting hash keys for {hash_name}: {e}")
            return []

    def hvals(self, hash_name: str) -> List[str]:
        """
        获取哈希表所有字段值
        :param hash_name: 哈希表名称
        :return: 字段值列表
        """
        try:
            return self.redis_client.hvals(hash_name)
        except Exception as e:
            print(f"Error getting hash values for {hash_name}: {e}")
            return []

    # ==================== List（列表）操作 ====================

    def lpush(self, key: str, *values: Any) -> Optional[int]:
        """
        从列表左端推入元素
        :param key: 列表键
        :param values: 要推入的值
        :return: 推入后的列表长度
        """
        try:
            return self.redis_client.lpush(key, *values)
        except Exception as e:
            print(f"Error lpush to list {key}: {e}")
            return None

    def rpush(self, key: str, *values: Any) -> Optional[int]:
        """
        从列表右端推入元素
        :param key: 列表键
        :param values: 要推入的值
        :return: 推入后的列表长度
        """
        try:
            return self.redis_client.rpush(key, *values)
        except Exception as e:
            print(f"Error rpush to list {key}: {e}")
            return None

    def lpop(self, key: str) -> Optional[str]:
        """
        从列表左端弹出元素
        :param key: 列表键
        :return: 弹出的元素
        """
        try:
            return self.redis_client.lpop(key)
        except Exception as e:
            print(f"Error lpop from list {key}: {e}")
            return None

    def rpop(self, key: str) -> Optional[str]:
        """
        从列表右端弹出元素
        :param key: 列表键
        :return: 弹出的元素
        """
        try:
            return self.redis_client.rpop(key)
        except Exception as e:
            print(f"Error rpop from list {key}: {e}")
            return None

    def lrange(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """
        获取列表指定范围的元素
        :param key: 列表键
        :param start: 起始索引，默认 0
        :param end: 结束索引，默认 -1（表示到列表末尾）
        :return: 元素列表
        """
        try:
            return self.redis_client.lrange(key, start, end)
        except Exception as e:
            print(f"Error lrange from list {key}: {e}")
            return []

    def llen(self, key: str) -> int:
        """
        获取列表长度
        :param key: 列表键
        :return: 列表长度
        """
        try:
            return self.redis_client.llen(key)
        except Exception as e:
            print(f"Error getting list length for {key}: {e}")
            return 0

    def ltrim(self, key: str, start: int, end: int) -> bool:
        """
        修剪列表，只保留指定范围的元素
        :param key: 列表键
        :param start: 起始索引
        :param end: 结束索引
        :return: 是否成功
        """
        try:
            self.redis_client.ltrim(key, start, end)
            return True
        except Exception as e:
            print(f"Error trimming list {key}: {e}")
            return False

    def lindex(self, key: str, index: int) -> Optional[str]:
        """
        获取列表指定索引的元素
        :param key: 列表键
        :param index: 索引
        :return: 元素值
        """
        try:
            return self.redis_client.lindex(key, index)
        except Exception as e:
            print(f"Error getting list index {index} for {key}: {e}")
            return None

    # ==================== Set（集合）操作 ====================

    def sadd(self, key: str, *members: Any) -> Optional[int]:
        """
        添加成员到集合
        :param key: 集合键
        :param members: 要添加的成员
        :return: 成功添加的成员数量
        """
        try:
            return self.redis_client.sadd(key, *members)
        except Exception as e:
            print(f"Error adding members to set {key}: {e}")
            return None

    def smembers(self, key: str) -> set:
        """
        获取集合所有成员
        :param key: 集合键
        :return: 成员集合
        """
        try:
            return self.redis_client.smembers(key)
        except Exception as e:
            print(f"Error getting set members for {key}: {e}")
            return set()

    def sismember(self, key: str, member: Any) -> bool:
        """
        判断元素是否在集合中
        :param key: 集合键
        :param member: 成员
        :return: 是否存在
        """
        try:
            return self.redis_client.sismember(key, member)
        except Exception as e:
            print(f"Error checking set membership for {key}: {e}")
            return False

    def srem(self, key: str, *members: Any) -> Optional[int]:
        """
        删除集合成员
        :param key: 集合键
        :param members: 要删除的成员
        :return: 成功删除的成员数量
        """
        try:
            return self.redis_client.srem(key, *members)
        except Exception as e:
            print(f"Error removing members from set {key}: {e}")
            return None

    def scard(self, key: str) -> int:
        """
        获取集合成员数量
        :param key: 集合键
        :return: 成员数量
        """
        try:
            return self.redis_client.scard(key)
        except Exception as e:
            print(f"Error getting set cardinality for {key}: {e}")
            return 0

    def sinter(self, *keys: str) -> set:
        """
        获取多个集合的交集
        :param keys: 集合键列表
        :return: 交集
        """
        try:
            return self.redis_client.sinter(*keys)
        except Exception as e:
            print(f"Error getting set intersection: {e}")
            return set()

    def sunion(self, *keys: str) -> set:
        """
        获取多个集合的并集
        :param keys: 集合键列表
        :return: 并集
        """
        try:
            return self.redis_client.sunion(*keys)
        except Exception as e:
            print(f"Error getting set union: {e}")
            return set()

    def sdiff(self, *keys: str) -> set:
        """
        获取多个集合的差集
        :param keys: 集合键列表
        :return: 差集
        """
        try:
            return self.redis_client.sdiff(*keys)
        except Exception as e:
            print(f"Error getting set difference: {e}")
            return set()

    def spop(
        self, key: str, count: Optional[int] = None
    ) -> Union[str, List[str], None]:
        """
        随机弹出集合成员
        :param key: 集合键
        :param count: 弹出数量，默认为 1
        :return: 弹出的成员
        """
        try:
            return self.redis_client.spop(key, count)
        except Exception as e:
            print(f"Error popping from set {key}: {e}")
            return None

    # ==================== Sorted Set（有序集合）操作 ====================

    def zadd(self, key: str, mapping: dict) -> Optional[int]:
        """
        添加成员和分数到有序集合
        :param key: 有序集合键
        :param mapping: 成员-分数映射字典，例如 {"member1": 1.0, "member2": 2.0}
        :return: 添加的成员数量
        """
        try:
            return self.redis_client.zadd(key, mapping)
        except Exception as e:
            print(f"Error adding members to sorted set {key}: {e}")
            return None

    def zrange(
        self, key: str, start: int = 0, end: int = -1, withscores: bool = False
    ) -> Union[List[str], List[tuple]]:
        """
        按分数升序获取有序集合成员
        :param key: 有序集合键
        :param start: 起始索引
        :param end: 结束索引
        :param withscores: 是否返回分数
        :return: 成员列表或 (成员, 分数) 元组列表
        """
        try:
            return self.redis_client.zrange(key, start, end, withscores=withscores)
        except Exception as e:
            print(f"Error getting zrange for {key}: {e}")
            return []

    def zrevrange(
        self, key: str, start: int = 0, end: int = -1, withscores: bool = False
    ) -> Union[List[str], List[tuple]]:
        """
        按分数降序获取有序集合成员
        :param key: 有序集合键
        :param start: 起始索引
        :param end: 结束索引
        :param withscores: 是否返回分数
        :return: 成员列表或 (成员, 分数) 元组列表
        """
        try:
            return self.redis_client.zrevrange(key, start, end, withscores=withscores)
        except Exception as e:
            print(f"Error getting zrevrange for {key}: {e}")
            return []

    def zscore(self, key: str, member: str) -> Optional[float]:
        """
        获取有序集合成员的分数
        :param key: 有序集合键
        :param member: 成员
        :return: 分数
        """
        try:
            return self.redis_client.zscore(key, member)
        except Exception as e:
            print(f"Error getting score for {member} in {key}: {e}")
            return None

    def zrem(self, key: str, *members: str) -> Optional[int]:
        """
        删除有序集合成员
        :param key: 有序集合键
        :param members: 要删除的成员
        :return: 删除的成员数量
        """
        try:
            return self.redis_client.zrem(key, *members)
        except Exception as e:
            print(f"Error removing members from sorted set {key}: {e}")
            return None

    def zincrby(self, key: str, amount: float, member: str) -> Optional[float]:
        """
        增加有序集合成员的分数
        :param key: 有序集合键
        :param amount: 增量
        :param member: 成员
        :return: 增加后的分数
        """
        try:
            return self.redis_client.zincrby(key, amount, member)
        except Exception as e:
            print(f"Error incrementing score for {member} in {key}: {e}")
            return None

    def zrank(self, key: str, member: str) -> Optional[int]:
        """
        获取有序集合成员的排名（升序）
        :param key: 有序集合键
        :param member: 成员
        :return: 排名（从 0 开始）
        """
        try:
            return self.redis_client.zrank(key, member)
        except Exception as e:
            print(f"Error getting rank for {member} in {key}: {e}")
            return None

    def zrevrank(self, key: str, member: str) -> Optional[int]:
        """
        获取有序集合成员的排名（降序）
        :param key: 有序集合键
        :param member: 成员
        :return: 排名（从 0 开始）
        """
        try:
            return self.redis_client.zrevrank(key, member)
        except Exception as e:
            print(f"Error getting reverse rank for {member} in {key}: {e}")
            return None

    def zcard(self, key: str) -> int:
        """
        获取有序集合成员数量
        :param key: 有序集合键
        :return: 成员数量
        """
        try:
            return self.redis_client.zcard(key)
        except Exception as e:
            print(f"Error getting sorted set cardinality for {key}: {e}")
            return 0

    def zcount(self, key: str, min_score: float, max_score: float) -> int:
        """
        获取有序集合指定分数范围的成员数量
        :param key: 有序集合键
        :param min_score: 最小分数
        :param max_score: 最大分数
        :return: 成员数量
        """
        try:
            return self.redis_client.zcount(key, min_score, max_score)
        except Exception as e:
            print(f"Error counting members in score range for {key}: {e}")
            return 0

    # ==================== TTL（过期时间）管理 ====================

    def expire(self, key: str, seconds: int) -> bool:
        """
        设置键的过期时间
        :param key: 键
        :param seconds: 过期时间（秒）
        :return: 是否成功
        """
        try:
            return self.redis_client.expire(key, seconds)
        except Exception as e:
            print(f"Error setting expire for key {key}: {e}")
            return False

    def ttl(self, key: str) -> int:
        """
        获取键的剩余过期时间
        :param key: 键
        :return: 剩余秒数，-1 表示永不过期，-2 表示键不存在
        """
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            print(f"Error getting TTL for key {key}: {e}")
            return -2

    def persist(self, key: str) -> bool:
        """
        移除键的过期时间，使其永久有效
        :param key: 键
        :return: 是否成功
        """
        try:
            return self.redis_client.persist(key)
        except Exception as e:
            print(f"Error persisting key {key}: {e}")
            return False

    def pexpire(self, key: str, milliseconds: int) -> bool:
        """
        设置键的过期时间（毫秒）
        :param key: 键
        :param milliseconds: 过期时间（毫秒）
        :return: 是否成功
        """
        try:
            return self.redis_client.pexpire(key, milliseconds)
        except Exception as e:
            print(f"Error setting pexpire for key {key}: {e}")
            return False

    def pttl(self, key: str) -> int:
        """
        获取键的剩余过期时间（毫秒）
        :param key: 键
        :return: 剩余毫秒数，-1 表示永不过期，-2 表示键不存在
        """
        try:
            return self.redis_client.pttl(key)
        except Exception as e:
            print(f"Error getting PTTL for key {key}: {e}")
            return -2

    # ==================== 键管理操作 ====================

    def keys(self, pattern: str = "*") -> List[str]:
        """
        查找匹配模式的键（生产环境慎用，建议使用 scan）
        :param pattern: 匹配模式，默认 "*"
        :return: 键列表
        """
        try:
            return self.redis_client.keys(pattern)
        except Exception as e:
            print(f"Error getting keys with pattern {pattern}: {e}")
            return []

    def scan(
        self, cursor: int = 0, match: Optional[str] = None, count: int = 10
    ) -> tuple:
        """
        迭代扫描键（推荐代替 keys 命令）
        :param cursor: 游标，从 0 开始
        :param match: 匹配模式
        :param count: 每次迭代返回的键数量建议值
        :return: (下一个游标, 键列表) 元组
        """
        try:
            return self.redis_client.scan(cursor=cursor, match=match, count=count)
        except Exception as e:
            print(f"Error scanning keys: {e}")
            return (0, [])

    def rename(self, old_key: str, new_key: str) -> bool:
        """
        重命名键
        :param old_key: 旧键名
        :param new_key: 新键名
        :return: 是否成功
        """
        try:
            self.redis_client.rename(old_key, new_key)
            return True
        except Exception as e:
            print(f"Error renaming key {old_key} to {new_key}: {e}")
            return False

    def type(self, key: str) -> Optional[str]:
        """
        获取键的类型
        :param key: 键
        :return: 类型字符串（string, list, set, zset, hash）
        """
        try:
            return self.redis_client.type(key)
        except Exception as e:
            print(f"Error getting type for key {key}: {e}")
            return None

    # ==================== 分布式锁 ====================

    def acquire_lock(
        self,
        lock_name: str,
        timeout: int = 10,
        retry_times: int = 3,
        retry_delay: float = 0.1,
    ) -> Optional[str]:
        """
        获取分布式锁
        :param lock_name: 锁名称
        :param timeout: 锁超时时间（秒）
        :param retry_times: 重试次数
        :param retry_delay: 重试延迟（秒）
        :return: 锁标识符（用于释放锁），获取失败返回 None
        """
        lock_key = f"lock:{lock_name}"
        identifier = str(uuid.uuid4())

        for _ in range(retry_times):
            try:
                # 使用 SET NX EX 原子操作获取锁
                if self.redis_client.set(lock_key, identifier, nx=True, ex=timeout):
                    return identifier
                time.sleep(retry_delay)
            except Exception as e:
                print(f"Error acquiring lock {lock_name}: {e}")
                return None

        return None

    def release_lock(self, lock_name: str, identifier: str) -> bool:
        """
        释放分布式锁
        :param lock_name: 锁名称
        :param identifier: 锁标识符（由 acquire_lock 返回）
        :return: 是否成功
        """
        lock_key = f"lock:{lock_name}"
        try:
            # 使用 Lua 脚本确保原子性：只有持有锁的客户端才能释放
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            result = self.redis_client.eval(lua_script, 1, lock_key, identifier)
            return bool(result)
        except Exception as e:
            print(f"Error releasing lock {lock_name}: {e}")
            return False
