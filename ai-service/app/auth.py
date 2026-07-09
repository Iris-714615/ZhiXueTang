"""JWT 鉴权依赖模块。

提供 FastAPI 依赖注入用的 ``verify_token`` 依赖，从请求头 ``Authorization``
中提取 Bearer Token 并使用 PyJWT 进行校验，实现与主业务后端
（Golang / Django）的跨服务统一鉴权。
"""
import jwt
from fastapi import Depends, Header, HTTPException, status

from app.config import JWT_SECRET, JWT_ALGORITHM


def verify_token(authorization: str = Header(...)) -> dict:
    """校验 Authorization 头中的 Bearer JWT Token。

    作为 FastAPI 依赖注入使用：``user: dict = Depends(verify_token)``。
    校验通过后返回 JWT payload（含 user_id、username 等声明），
    校验失败抛出 401 HTTPException。

    Args:
        authorization: 请求头 ``Authorization`` 的值，格式应为 ``Bearer <token>``。

    Returns:
        dict: 解码后的 JWT payload。

    Raises:
        HTTPException: 当请求头缺失、格式错误或 Token 无效时返回 401。
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 校验 Bearer 前缀并提取 token 部分
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证信息格式错误，应为 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]

    # 使用 PyJWT 校验签名与有效期
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
