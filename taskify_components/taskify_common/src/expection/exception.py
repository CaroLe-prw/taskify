from ..expection.exception_code import Code, get_message


class TaskifyException(Exception):
    """通用自定义异常"""

    def __init__(self, code: int, message: str = get_message(Code.FAIL)):
        super().__init__(message)
        self.message = message
        self.code = code


class WalletException(TaskifyException):
    """钱包自定义异常"""

    def __init__(self, code, message: str = get_message(Code.FAIL)):
        super().__init__(code, message)


class DataException(TaskifyException):
    """数据自定义异常"""

    def __init__(self, code, message: str = get_message(Code.FAIL)):
        super().__init__(code, message)


class AuthException(TaskifyException):
    """认证自定义异常"""

    def __init__(self, code, message: str = get_message(Code.FAIL)):
        super().__init__(code, message)
