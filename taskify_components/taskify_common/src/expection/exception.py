class TaskifyException(Exception):
    """通用自定义异常"""

    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.message = message
        self.code = code


class WalletException(TaskifyException):
    """钱包自定义异常"""

    def __init__(self, message, code):
        super().__init__(message, code)


class DataException(TaskifyException):
    """数据自定义异常"""

    def __init__(self, message, code):
        super().__init__(message, code)
