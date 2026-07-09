"""
微信支付配置文件
"""

class WxPayConfig:
    # 商户号
    MCH_ID = "1558950191"
    # 商户API证书序列号
    MCH_SERIAL_NO = "34345964330B66427E0D3D28826C4993C77E631F"
    # 商户私钥文件
    PRIVATE_KEY_PATH = "tcourse/apiclient_key.pem"
    # APIv3密钥
    API_V3_KEY = "UDuLFDcmy5Eb6o0nTNZdu6ek4DDh4K8B"
    # APPID
    APP_ID = "wx74862e0dfcf69954"
    # 微信服务器地址
    DOMAIN = "https://api.mch.weixin.qq.com"
    # 接收结果通知地址
    NOTIFY_DOMAIN = "https://500c-219-143-130-12.ngrok.io"
    # APIv2密钥
    PARTNER_KEY = "T6m9iK73b0kn9g5v426MKfHQH7X8rKwb"

    # API地址
    NATIVE_ORDER_URL = f"{DOMAIN}/v3/pay/transactions/native"  # Native下单
    QUERY_ORDER_URL = f"{DOMAIN}/v3/pay/transactions/id/"  # 查询订单
    CLOSE_ORDER_URL = f"{DOMAIN}/v3/pay/transactions/out-trade-no/%s/close"  # 关闭订单
    REFUND_URL = f"{DOMAIN}/v3/refund/domestic/refunds"  # 申请退款
    QUERY_REFUND_URL = f"{DOMAIN}/v3/refund/domestic/refunds/%s"  # 查询单笔退款