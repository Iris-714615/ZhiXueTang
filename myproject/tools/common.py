import bcrypt

def encrypt_password(password):
    """密码加密"""
    # 生成随机盐
    salt = bcrypt.gensalt()
    # 哈希加密
    pwd_bytes = password.encode("utf-8")
    hash_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hash_bytes.decode("utf-8")

def check_password(password, hash_str):
    
    """密码校验"""
    pwd_bytes = password.encode("utf-8")
    hash_bytes = hash_str.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hash_bytes)

from .pay import AliPay
#初始化阿里支付对象
def get_alipay():
    # 沙箱环境地址：https://openhome.alipay.com/platform/appDaily.htm?tab=info
    app_id = "9021000163650098"  #  APPID （沙箱应用）

    # 支付完成后，支付偷偷向这里地址发送一个post请求，识别公网IP,如果是 192.168.20.13局域网IP ,支付宝找不到，def page2() 接收不到这个请求
    notify_url = "http://localhost:8000/tcourse/alipaycallback/"

    # 支付完成后，跳转的地址。
    return_url = "http://localhost:8000/tcourse/alipaycallback/"

    merchant_private_key_path = "E:/AICM/demo/p3/myproject/keys/private.txt" # 应用私钥
    alipay_public_key_path = "E:/AICM/demo/p3/myproject/keys/public.txt"  # 支付宝公钥

    alipay = AliPay(
        appid=app_id,
        app_notify_url=notify_url,
        return_url=return_url,
        app_private_key_path=merchant_private_key_path,
        alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        debug=True,  # 默认False,
    )
    return alipay

