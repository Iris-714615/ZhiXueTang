import redis
class MyRedis:
    def __init__(self):
        # 使用StrictRedis确保操作一致性
        self.r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=False)
   

    def set(self,key,value):
        try:
            self.r.set(key,value)
  
            return True
        except Exception as e:

            return False

    def get(self,key):
        value = self.r.get(key)
   
        return value
        
    def delete(self,key):
        try:
            result = self.r.delete(key)
        
            return True
        except Exception as e:
       
            return False

    def setex(self,key,expire,value):
        try:
            self.r.setex(key,expire,value)           
            # 验证TTL
            ttl = self.r.ttl(key)
            return True
        except Exception as e:
            return False

    def setnx(self,key,value):
        try:
            result = self.r.setnx(key,value)
            return True
        except Exception as e:
            return False
        
    def setnxex(self,key,value,expire=30):
        return self.r.set(key,value,nx=True,ex=expire)

    def hset(self,key,field,value):
        try:
            self.r.hset(key,field,value)
            return True
        except Exception as e:
            return False
    # 设置多个字段
    def hmset(self,key,fields):
        try:
            self.r.hmset(key,fields)
            return True
        except Exception as e:
            return False

    #获取单个属性值
    def hget(self,key,field):
        try:
            value = self.r.hget(key,field)
            return value
        except Exception as e:
            return False
    #获取所有属性值/整个对象的属性和值
    def hgetall(self,key):
        try:
            values = self.r.hgetall(key)
            return values if values is not None else {}
        except Exception as e:
            print(f"Redis hgetall错误: {e}")
            return {}

    #判断字段是否存在
    def hexists(self,key,field):
        if not self.r:
            return False
        try:
            return self.r.hexists(key,field)
        except Exception as e:
            print(f"Redis hexists错误: {e}")
            return False
    
    #删除hash字段
    def hdel(self,key,field):
        if not self.r:
            return False
        try:
            self.r.hdel(key,field)
            return True
        except Exception as e:
            print(f"Redis hdel错误: {e}")
            return False

    def hdelall(self,key,*fields):
        if not self.r:
            return False
        try:
            # Redis的hdel本身就支持删除多个字段
            if fields:
                self.r.hdel(key,*fields)
            return True
        except Exception as e:
            print(f"Redis hdelall错误: {e}")
            return False
    #设置过期时间
    def expire(self,key,expire):
        try:
            self.r.expire(key,expire)
            return True
        except Exception as e:
            return False

    # list添加
    def lpush(self,key,value):
        try:
            self.r.lpush(key,value)  #.append()
            return True
        except Exception as e:
            print(f"Redis lpush错误: {e}")
            return False

    #删除list指定范围的元素
# count > 0：从左往右，删 前 count 个 匹配 value
# count < 0：从右往左，删 后 |count| 个 匹配 value
# count = 0：删除所有 匹配 value 的元素
    def lrem(self,key,count,value):
        try:
            self.r.lrem(key,0,str(value))
            return True
        except Exception as e:
            print(f"Redis lrem错误: {e}")
            return False
    #获取list长度
    def llen(self,key):
        try:
            length = self.r.llen(key)
            return length
        except Exception as e:
            print(f"Redis llen错误: {e}")
            return False
    #获取list元素
    def lrange(self,key,start,end):
        try:
            values = self.r.lrange(key,start,end)
            return values
        except Exception as e:
            print(f"Redis lrange错误: {e}")
            return False
r = MyRedis()



