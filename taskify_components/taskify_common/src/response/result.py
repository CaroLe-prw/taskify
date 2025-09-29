from typing import Any, Optional

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Result(BaseModel):
    """统一响应结果类"""

    code: int = 200
    message: str = "success"
    data: Optional[Any] = None

    def to_response(self) -> JSONResponse:
        """转换为JSONResponse"""
        return JSONResponse(content=self.model_dump())

    @classmethod
    def success(cls, data: Any = None, message: str = "success") -> JSONResponse:
        """成功响应，直接返回JSONResponse"""
        result = cls(code=200, message=message, data=data)
        return result.to_response()

    @classmethod
    def fail(
        cls, code: int = 500, message: str = "fail", data: Any = None
    ) -> JSONResponse:
        """错误响应，直接返回JSONResponse"""
        result = cls(code=code, message=message, data=data)
        return result.to_response()
