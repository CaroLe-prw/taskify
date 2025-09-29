from fastapi import HTTPException, Request

from .exception import TaskifyException
from .exception_code import Code, get_message
from ..logger.logger import log_error
from ..response import Result


def register_exception_handlers(app):
    """注册公共异常"""

    @app.exception_handler(TaskifyException)
    async def data_exception_handler(request: Request, exc: TaskifyException):
        # 获取错误信息，如果没有自定义message则使用预定义的
        error_message = (
            exc.message if exc.message else get_message(exc.code, "未知错误")
        )

        log_error(
            f"自定义异常 - 错误码: {exc.code}, "
            f"错误信息: {error_message}, "
            f"请求方法: {request.method}, "
            f"请求路径: {request.url.path}, "
            f"查询参数: {request.url.query}"
        )
        return Result.fail(code=exc.code, message=error_message)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # 使用HTTP状态码或获取预定义消息
        error_message = (
            str(exc.detail) if exc.detail else get_message(exc.status_code, "HTTP错误")
        )

        log_error(
            f"HTTP异常 - 状态码: {exc.status_code}, "
            f"错误信息: {error_message}, "
            f"请求方法: {request.method}, "
            f"请求路径: {request.url.path}, "
            f"查询参数: {request.url.query}"
        )
        return Result.fail(code=exc.status_code, message=error_message)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        import traceback

        # 获取详细的异常堆栈信息
        error_trace = traceback.format_exc()
        error_detail = str(exc) if str(exc) else "未知异常"

        log_error(
            f"未捕获的全局异常 - "
            f"异常类型: {type(exc).__name__}, "
            f"异常信息: {error_detail}, "
            f"请求方法: {request.method}, "
            f"请求路径: {request.url.path}, "
            f"查询参数: {request.url.query}, "
            f"异常堆栈:\n{error_trace}"
        )

        # 使用预定义的服务器错误码
        return Result.fail(
            code=Code.INTERNAL_SERVER_ERROR,
            message=get_message(Code.INTERNAL_SERVER_ERROR),
        )
