import os
import jwt
import datetime
import secrets

class MyJWT:
    def __init__(self, secret_key=None, algorithm='HS256'):
        """
        初始化JWT工具类
        :param secret_key: 密钥，如果为None则自动生成
        :param algorithm: 加密算法，默认HS256
        """
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = algorithm
    
    def encode(self, payload, expire_seconds=60*60*24):
        """
        生成JWT token
        :param payload: 要编码的数据
        :param expire_seconds: 过期时间（秒），默认1天
        :return: JWT token字符串
        """
        # 添加过期时间
        payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(seconds=expire_seconds)
        payload['iat'] = datetime.datetime.utcnow()#签发时间 issued at
        
        try:
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
        except Exception as e:
            print(f'生成token失败: {e}')
            return None
    
    def decode(self, token):
        """
        解码JWT token
        :param token: JWT token字符串
        :return: 解码后的数据，如果token无效则返回None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            print('token已过期')
            return None
        except jwt.InvalidTokenError:
            print('无效的token')
            return None
        except Exception as e:
            print(f'解码token失败: {e}')
            return None
    
    def verify(self, token):
        """
        验证JWT token
        :param token: JWT token字符串
        :return: bool，token是否有效
        """
        payload = self.decode(token)
        return payload is not None

# 创建全局实例
myjwt = MyJWT(secret_key=os.getenv("JWT_SECRET", "ZhiHu-ZhiXueTang-Secret-Key"))
