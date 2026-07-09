# import json
# import time
# import uuid
# import requests
# from datetime import datetime
# from Crypto.Hash import SHA256
# from Crypto.PublicKey import RSA
# from Crypto.Signature import pkcs1_15
# from Crypto.Cipher import AES
# from base64 import b64encode, b64decode
# import logging
# from .config import WxPayConfig

# logger = logging.getLogger('django')

# class WxPayClient:
#     """微信支付客户端"""

#     def __init__(self):
#         self.config = WxPayConfig()
#         # 读取商户私钥
#         with open(self.config.PRIVATE_KEY_PATH) as f:
#             self.private_key = RSA.import_key(f.read())

#     def sign(self, method, url_path, body):
#         """生成请求签名
#         :param method: 请求方法（GET、POST等）
#         :param url_path: 请求路径
#         :param body: 请求体
#         :return: 签名
#         """
#         timestamp = str(int(time.time()))
#         nonce = str(uuid.uuid4()).replace('-', '')

#         # 构造签名信息
#         sign_str = f"{method}\n{url_path}\n{timestamp}\n{nonce}\n{body}\n"
#         # 计算签名
#         h = SHA256.new(sign_str.encode('utf-8'))
#         signature = pkcs1_15.new(self.private_key).sign(h)

#         # 设置认证信息
#         token = f'WECHATPAY2-SHA256-RSA2048 mchid="{self.config.MCH_ID}",nonce_str="{nonce}",timestamp="{timestamp}",serial_no="{self.config.MCH_SERIAL_NO}",signature="{b64encode(signature).decode()}"'
#         return token

#     def create_order(self, order_number, total_fee, description):
#         """创建Native支付订单
#         :param order_number: 商户订单号
#         :param total_fee: 订单金额（单位：分）
#         :param description: 商品描述
#         :return: 支付二维码链接
#         """
#         url = self.config.NATIVE_ORDER_URL
#         url_path = url.split(self.config.DOMAIN)[-1]

#         data = {
#             "appid": self.config.APP_ID,
#             "mchid": self.config.MCH_ID,
#             "description": description,
#             "out_trade_no": order_number,
#             "notify_url": f"{self.config.NOTIFY_DOMAIN}/payment/wx/notify/",
#             "amount": {
#                 "total": total_fee,
#                 "currency": "CNY"
#             }
#         }

#         # 将请求参数转换为JSON字符串
#         body = json.dumps(data)
#         logger.info(f"微信支付下单请求：{body}")
#         # 生成认证签名
#         token = self.sign('POST', url_path, body)

#         # 发送请求
#         headers = {
#             'Content-Type': 'application/json',
#             'Accept': 'application/json',
#             'Authorization': token
#         }

#         try:
#             response = requests.post(url, data=body, headers=headers)
#             result = response.json()
#             logger.info(f"微信支付下单响应：{result}")

#             if 'code_url' in result:
#                 return result['code_url']
#             else:
#                 logger.error(f"微信支付下单失败：{result}")
#                 return None
#         except Exception as e:
#             logger.error(f"微信支付下单异常：{str(e)}")
#             return None

#     # -------------------- 回调验签与解密 --------------------

#     def verify_callback_signature(self, headers: dict, body: str) -> bool:
#         """
#         验证微信回调签名（可选：当配置了平台公钥时启用）。
#         需要请求头：Wechatpay-Timestamp, Wechatpay-Nonce, Wechatpay-Signature, Wechatpay-Serial
#         """
#         try:
#             platform_public_key_path = getattr(WxPayConfig, 'WECHAT_PLATFORM_PUBLIC_KEY_PATH', None)
#             if not platform_public_key_path:
#                 # 未配置平台证书时，跳过验签（视需求调整为严格模式）
#                 return True

#             timestamp = headers.get('Wechatpay-Timestamp') or headers.get('WECHATPAY-TIMESTAMP')
#             nonce = headers.get('Wechatpay-Nonce') or headers.get('WECHATPAY-NONCE')
#             signature_b64 = headers.get('Wechatpay-Signature') or headers.get('WECHATPAY-SIGNATURE')

#             if not timestamp or not nonce or not signature_b64:
#                 return False

#             message = f"{timestamp}\n{nonce}\n{body}\n"
#             signature = b64decode(signature_b64)

#             with open(platform_public_key_path, 'rb') as f:
#                 platform_public_key = RSA.import_key(f.read())

#             h = SHA256.new(message.encode('utf-8'))
#             pkcs1_15.new(platform_public_key).verify(h, signature)
#             return True
#         except Exception as e:
#             logger.error(f"微信回调验签失败: {e}")
#             return False

#     def decrypt_notification(self, resource: dict) -> dict:
#         """
#         使用 APIv3 密钥对回调资源体进行 AES-256-GCM 解密
#         """
#         api_v3_key = WxPayConfig.API_V3_KEY
#         ciphertext_b64 = resource.get('ciphertext')
#         nonce = resource.get('nonce')
#         associated_data = resource.get('associated_data', '')

#         if not api_v3_key or not ciphertext_b64 or not nonce:
#             raise ValueError('回调解密参数缺失')

#         key_bytes = api_v3_key.encode('utf-8')
#         cipher_bytes = b64decode(ciphertext_b64)
#         nonce_bytes = nonce.encode('utf-8')
#         aad_bytes = associated_data.encode('utf-8') if associated_data else b''

#         if len(cipher_bytes) < 16:
#             raise ValueError('密文长度非法')
#         data_bytes, tag_bytes = cipher_bytes[:-16], cipher_bytes[-16:]

#         cipher = AES.new(key_bytes, AES.MODE_GCM, nonce=nonce_bytes)
#         if aad_bytes:
#             cipher.update(aad_bytes)
#         plaintext = cipher.decrypt_and_verify(data_bytes, tag_bytes)
#         return json.loads(plaintext.decode('utf-8'))

#     def query_order(self, order_number):
#         """查询订单状态
#         :param order_number: 商户订单号
#         :return: 订单信息
#         """
#         url = f"{self.config.DOMAIN}/v3/pay/transactions/out-trade-no/{order_number}?mchid={self.config.MCH_ID}"
#         url_path = url.split(self.config.DOMAIN)[-1]

#         # 生成认证签名
#         token = self.sign('GET', url_path, '')

#         # 发送请求
#         headers = {
#             'Accept': 'application/json',
#             'Authorization': token
#         }

#         try:
#             response = requests.get(url, headers=headers)
#             result = response.json()
#             logger.info(f"微信支付查询订单响应：{result}")
#             return result
#         except Exception as e:
#             logger.error(f"微信支付查询订单异常：{str(e)}")
#             return None

#     def close_order(self, order_number):
#         """关闭订单
#         :param order_number: 商户订单号
#         :return: 是否成功
#         """
#         url = self.config.CLOSE_ORDER_URL % order_number
#         url_path = url.split(self.config.DOMAIN)[-1]

#         data = {"mchid": self.config.MCH_ID}
#         body = json.dumps(data)

#         # 生成认证签名
#         token = self.sign('POST', url_path, body)

#         # 发送请求
#         headers = {
#             'Content-Type': 'application/json',
#             'Accept': 'application/json',
#             'Authorization': token
#         }

#         try:
#             response = requests.post(url, data=body, headers=headers)
#             if response.status_code == 204:
#                 return True
#             else:
#                 logger.error(f"微信支付关闭订单失败：{response.text}")
#                 return False
#         except Exception as e:
#             logger.error(f"微信支付关闭订单异常：{str(e)}")
#             return False