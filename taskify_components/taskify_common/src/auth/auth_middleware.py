from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from ..expection.exception import AuthException
from ..expection.exception_code import Code
from .token_helper import TokenHelper


class AuthCORSMiddleware(BaseHTTPMiddleware):
    """token cors校验中间件"""

    def __init__(self, app, token_helper: TokenHelper):
        """
        初始化中间件
        :param app: ASGI 应用
        :param token_helper: TokenHelper 实例
        """
        super().__init__(app)
        self.token_helper = token_helper

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:

        # 检查请求头中是否携带 Token
        authorization_token = request.headers.get("Authorization")

        if not authorization_token:
            raise AuthException(code=Code.UNAUTHORIZED)

        # 检查 Token 格式
        if not authorization_token.startswith("Bearer "):
            raise AuthException(code=Code.UNAUTHORIZED)

        # 提取 token（去掉 "Bearer " 前缀）
        token = authorization_token[7:]

        # 验证 token 有效性
        if not self.token_helper.verify_token(token, token_type="access"):
            raise AuthException(code=Code.UNAUTHORIZED)

        # 解析 token 获取用户信息
        user_info = self.token_helper.decode_token(token)
        if not user_info:
            raise AuthException(code=Code.UNAUTHORIZED)

        # 将用户信息存入 request.state，方便后续使用
        request.state.user_id = user_info.get("user_id")
        request.state.user_info = user_info

        # 继续处理请求
        response = await call_next(request)

        # 添加 CORS 相关的响应头
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST,DELETE,PUT"
        response.headers["Access-Control-Allow-Headers"] = "*"

        return response
