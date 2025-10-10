from passlib.context import CryptContext

# 创建一个 CryptContext 对象
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHelper:

    @staticmethod
    def get_password_hash(password: str) -> str:
        """将密码加密"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码是否匹配"""
        return pwd_context.verify(plain_password, hashed_password)
