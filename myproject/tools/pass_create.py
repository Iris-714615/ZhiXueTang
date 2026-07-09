import bcrypt

def hash_password(password):
    """密码加密"""
    # 生成随机盐
    salt = bcrypt.gensalt()
    # 哈希加密
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def check_password(hashed_password, user_password):
    """Check a plain text password against a hashed one."""
    pwd_bytes = user_password.encode("utf-8")
    hash_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hash_bytes)