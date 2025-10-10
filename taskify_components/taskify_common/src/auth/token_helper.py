from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from taskify_redis import RedisHelper


class TokenHelper:
    """Token 管理工具类，支持 JWT + Redis"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        redis_helper: Optional[RedisHelper] = None,
    ):
        """
        初始化 TokenHelper
        :param secret_key: JWT 密钥
        :param algorithm: 加密算法，默认 HS256
        :param access_token_expire_minutes: access token 过期时间（分钟），默认 30 分钟
        :param refresh_token_expire_days: refresh token 过期时间（天），默认 7 天
        :param redis_helper: Redis 工具类实例，用于存储 token 黑名单等
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.redis_helper = redis_helper

    def generate_token(
        self, user_id: str, user_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成 access token
        :param user_id: 用户 ID
        :param user_data: 用户额外数据（如用户名、角色等）
        :return: access token 字符串
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)

        payload = {
            "user_id": user_id,
            "exp": expire,
            "iat": now,
            "type": "access",
        }

        # 合并用户数据
        if user_data:
            payload.update(user_data)

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def generate_refresh_token(self, user_id: str) -> str:
        """
        生成 refresh token
        :param user_id: 用户 ID
        :return: refresh token 字符串
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "user_id": user_id,
            "exp": expire,
            "iat": now,
            "type": "refresh",
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        # 将 refresh token 存入 Redis
        if self.redis_helper:
            redis_key = f"refresh_token:{user_id}"
            expire_seconds = self.refresh_token_expire_days * 24 * 60 * 60
            self.redis_helper.set(redis_key, token, ex=expire_seconds, serialize=False)

        return token

    def verify_token(self, token: str, token_type: str = "access") -> bool:
        """
        验证 token 是否有效
        :param token: token 字符串
        :param token_type: token 类型（access 或 refresh）
        :return: 是否有效
        """
        try:
            # 检查 token 是否在黑名单中
            if self.redis_helper and self._is_token_blacklisted(token):
                return False

            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # 验证 token 类型
            if payload.get("type") != token_type:
                return False

            return True
        except jwt.ExpiredSignatureError:
            # Token 已过期
            return False
        except jwt.InvalidTokenError:
            # Token 无效
            return False
        except Exception:
            return False

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        解析 token 获取用户信息
        :param token: token 字符串
        :return: 用户信息字典，失败返回 None
        """
        try:
            # 检查 token 是否在黑名单中
            if self.redis_helper and self._is_token_blacklisted(token):
                return None

            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            # Token 已过期
            return None
        except jwt.InvalidTokenError:
            # Token 无效
            return None
        except Exception:
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        使用 refresh token 刷新 access token
        :param refresh_token: refresh token 字符串
        :return: 新的 access token，失败返回 None
        """
        # 验证 refresh token
        if not self.verify_token(refresh_token, token_type="refresh"):
            return None

        # 解析 refresh token 获取用户信息
        payload = self.decode_token(refresh_token)
        if not payload:
            return None

        user_id = payload.get("user_id")
        if not user_id:
            return None

        # 如果使用 Redis 存储，验证 refresh token 是否匹配
        if self.redis_helper:
            redis_key = f"refresh_token:{user_id}"
            stored_token = self.redis_helper.get(redis_key, deserialize=False)
            if stored_token != refresh_token:
                return None

        # 生成新的 access token
        # 保留原 payload 中的用户数据（排除系统字段）
        user_data = {
            k: v
            for k, v in payload.items()
            if k not in ["user_id", "exp", "iat", "type"]
        }
        new_access_token = self.generate_token(user_id, user_data)

        return new_access_token

    def revoke_token(self, token: str) -> bool:
        """
        撤销 token（加入黑名单）
        :param token: 要撤销的 token
        :return: 是否成功
        """
        if not self.redis_helper:
            return False

        try:
            # 解析 token 获取过期时间
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False},  # 不验证过期时间
            )
            exp = payload.get("exp")
            if not exp:
                return False

            # 计算剩余过期时间
            now = datetime.now(timezone.utc).timestamp()
            ttl = int(exp - now)
            if ttl <= 0:
                return True  # 已过期的 token 无需加入黑名单

            # 将 token 加入黑名单
            blacklist_key = f"token_blacklist:{token}"
            self.redis_helper.set(blacklist_key, "1", ex=ttl, serialize=False)
            return True
        except Exception as e:
            print(f"Error revoking token: {e}")
            return False

    def revoke_user_tokens(self, user_id: str) -> bool:
        """
        撤销用户的所有 refresh token
        :param user_id: 用户 ID
        :return: 是否成功
        """
        if not self.redis_helper:
            return False

        try:
            redis_key = f"refresh_token:{user_id}"
            return self.redis_helper.delete(redis_key)
        except Exception as e:
            print(f"Error revoking user tokens: {e}")
            return False

    def _is_token_blacklisted(self, token: str) -> bool:
        """
        检查 token 是否在黑名单中
        :param token: token 字符串
        :return: 是否在黑名单中
        """
        if not self.redis_helper:
            return False

        blacklist_key = f"token_blacklist:{token}"
        return self.redis_helper.exists(blacklist_key)
