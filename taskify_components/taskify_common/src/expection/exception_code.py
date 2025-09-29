"""
异常状态码定义
统一管理所有的异常状态码，方便维护和使用
"""


class Code:
    """状态码常量类"""

    # ============ 通用状态码 ============
    # 成功
    SUCCESS = 200

    # 失败
    FAIL = 500

    # ============ 客户端错误 4xx ============
    # 请求参数错误
    BAD_REQUEST = 400

    # 未授权
    UNAUTHORIZED = 401

    # 禁止访问
    FORBIDDEN = 403

    # 资源未找到
    NOT_FOUND = 404

    # 请求方法不允许
    METHOD_NOT_ALLOWED = 405

    # 请求超时
    REQUEST_TIMEOUT = 408

    # 请求冲突
    CONFLICT = 409

    # 请求参数验证失败
    UNPROCESSABLE_ENTITY = 422

    # 请求次数过多
    TOO_MANY_REQUESTS = 429

    # ============ 服务端错误 5xx ============
    # 服务器内部错误
    INTERNAL_SERVER_ERROR = 500

    # 服务不可用
    SERVICE_UNAVAILABLE = 503

    # 网关超时
    GATEWAY_TIMEOUT = 504

    # ============ 业务错误码 10000+ ============
    # 用户相关 10001-10999
    USER_NOT_FOUND = 10001
    USER_ALREADY_EXISTS = 10002
    USER_PASSWORD_ERROR = 10003
    USER_DISABLED = 10004
    USER_TOKEN_EXPIRED = 10005
    USER_TOKEN_INVALID = 10006

    # 订单相关 11001-11999
    ORDER_NOT_FOUND = 11001
    ORDER_ALREADY_PAID = 11002
    ORDER_EXPIRED = 11003
    ORDER_CANCELLED = 11004
    ORDER_AMOUNT_ERROR = 11005

    # 商品相关 12001-12999
    PRODUCT_NOT_FOUND = 12001
    PRODUCT_STOCK_INSUFFICIENT = 12002
    PRODUCT_OFFLINE = 12003
    PRODUCT_PRICE_ERROR = 12004

    # 支付相关 13001-13999
    PAYMENT_FAILED = 13001
    PAYMENT_TIMEOUT = 13002
    PAYMENT_CANCELLED = 13003
    PAYMENT_AMOUNT_ERROR = 13004
    PAYMENT_METHOD_NOT_SUPPORTED = 13005

    # 钱包相关 14001-14999
    WALLET_BALANCE_INSUFFICIENT = 14001
    WALLET_NOT_FOUND = 14002
    WALLET_FROZEN = 14003
    WALLET_TRANSACTION_FAILED = 14004

    # 数据相关 15001-15999
    DATA_NOT_FOUND = 15001
    DATA_DUPLICATE = 15002
    DATA_FORMAT_ERROR = 15003
    DATA_VALIDATION_ERROR = 15004


# 错误信息映射
ERROR_MESSAGES = {
    Code.SUCCESS: "成功",
    Code.FAIL: "失败",
    Code.BAD_REQUEST: "请求参数错误",
    Code.UNAUTHORIZED: "未授权",
    Code.FORBIDDEN: "禁止访问",
    Code.NOT_FOUND: "资源未找到",
    Code.METHOD_NOT_ALLOWED: "请求方法不允许",
    Code.REQUEST_TIMEOUT: "请求超时",
    Code.CONFLICT: "请求冲突",
    Code.UNPROCESSABLE_ENTITY: "请求参数验证失败",
    Code.TOO_MANY_REQUESTS: "请求次数过多",
    Code.INTERNAL_SERVER_ERROR: "服务器内部错误",
    Code.SERVICE_UNAVAILABLE: "服务不可用",
    Code.GATEWAY_TIMEOUT: "网关超时",
    # 用户相关
    Code.USER_NOT_FOUND: "用户不存在",
    Code.USER_ALREADY_EXISTS: "用户已存在",
    Code.USER_PASSWORD_ERROR: "用户密码错误",
    Code.USER_DISABLED: "用户已禁用",
    Code.USER_TOKEN_EXPIRED: "用户令牌已过期",
    Code.USER_TOKEN_INVALID: "用户令牌无效",
    # 订单相关
    Code.ORDER_NOT_FOUND: "订单不存在",
    Code.ORDER_ALREADY_PAID: "订单已支付",
    Code.ORDER_EXPIRED: "订单已过期",
    Code.ORDER_CANCELLED: "订单已取消",
    Code.ORDER_AMOUNT_ERROR: "订单金额错误",
    # 商品相关
    Code.PRODUCT_NOT_FOUND: "商品不存在",
    Code.PRODUCT_STOCK_INSUFFICIENT: "商品库存不足",
    Code.PRODUCT_OFFLINE: "商品已下架",
    Code.PRODUCT_PRICE_ERROR: "商品价格错误",
    # 支付相关
    Code.PAYMENT_FAILED: "支付失败",
    Code.PAYMENT_TIMEOUT: "支付超时",
    Code.PAYMENT_CANCELLED: "支付已取消",
    Code.PAYMENT_AMOUNT_ERROR: "支付金额错误",
    Code.PAYMENT_METHOD_NOT_SUPPORTED: "支付方式不支持",
    # 钱包相关
    Code.WALLET_BALANCE_INSUFFICIENT: "钱包余额不足",
    Code.WALLET_NOT_FOUND: "钱包不存在",
    Code.WALLET_FROZEN: "钱包已冻结",
    Code.WALLET_TRANSACTION_FAILED: "钱包交易失败",
    # 数据相关
    Code.DATA_NOT_FOUND: "数据不存在",
    Code.DATA_DUPLICATE: "数据重复",
    Code.DATA_FORMAT_ERROR: "数据格式错误",
    Code.DATA_VALIDATION_ERROR: "数据验证错误",
}


def get_message(code: int, default: str = None) -> str:
    """
    根据状态码获取错误信息

    Args:
        code: 状态码
        default: 默认错误信息

    Returns:
        错误信息
    """
    return ERROR_MESSAGES.get(code, default or f"未知错误 (code: {code})")
