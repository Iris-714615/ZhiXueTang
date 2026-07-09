from django.db import models

# Create your models here.

# 老师表   Id  姓名 职位 简介  头像
class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    position = models.CharField(max_length=20)
    introduction = models.TextField()
    avatar = models.ImageField(upload_to='avatar')
    class Meta:
        db_table = 'teacher'

# 课程表   Id  图片  名称  原价  优惠   总人数   总课时  老师 id（外键关联老师表）
class Course(models.Model):
    id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='course')
    name = models.CharField(max_length=20)
    original_price = models.FloatField()
    discount_price = models.FloatField()
    total_people = models.IntegerField()
    total_classes = models.IntegerField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    class Meta:
        db_table = 'course'

# 用户表   Id  手机号  密码  昵称  头像
class TUser(models.Model):
    id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    nickname = models.CharField(max_length=20)
    avatar = models.ImageField(upload_to='avatar')
    class Meta:
        db_table = 'user'

# 订单表   订单号（主键约束）  添加时间  用户 id  总金额
class Order(models.Model):
    order_no = models.CharField(max_length=50, primary_key=True)
    add_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.FloatField()
    class Meta:
        db_table = 'order'

# 订单详情表  Id  订单号（外键关联订单表） 课程 id    课程名  课程价格  数量  金额  状态
class OrderDetail(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    price = models.FloatField()
    quantity = models.IntegerField()
    total_price = models.FloatField()
    status = models.CharField(max_length=20)
    class Meta:
        db_table = 'order_detail'
