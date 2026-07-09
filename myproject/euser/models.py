from django.db import models
from tools.models import BaseModel

# Create your models here.

class User(BaseModel):
    """用户表"""
    username = models.CharField(max_length=32, verbose_name="用户名",unique=True)
    password = models.CharField(max_length=255, verbose_name="密码")
    phone = models.CharField(max_length=11, verbose_name="手机号",unique=True)
    email = models.EmailField(max_length=64, verbose_name="邮箱", null=True, blank=True)
    points = models.IntegerField(default=0, verbose_name="积分")
    account = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="余额")
    avatar = models.ImageField(upload_to="avatar/", verbose_name="头像", null=True, blank=True)
    
    class Meta:
        db_table = "tuser"
        verbose_name = "用户"
        verbose_name_plural = "用户"
    
    def __str__(self):
        return self.username

# id 用户id  课程id 类型 开始时间  到期时间 状态（1未开始 2学习中 3已完成） 学习总时长  学习进度   是否收藏（默认为否）
class MyCourse(BaseModel):
    """我的课程表"""
    user = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='用户')
    course = models.ForeignKey("tcourse.Courses",on_delete=models.CASCADE, verbose_name='课程')
    course_type = models.IntegerField(choices=[(1,'永久有效'),(2,'一个月'),(3,'一年'),(4,'2年')], default=1, verbose_name='课程类型')
    start_time = models.DateTimeField(verbose_name='开始时间',null=True, blank=True)
    end_time = models.DateTimeField(verbose_name='到期时间',null=True, blank=True)
    status = models.IntegerField(choices=[(1, '未开始'), (2, '学习中'), (3, '已完成'),(4,'已退款')], default=1, verbose_name='状态')
    total_time = models.IntegerField(default=0, verbose_name='学习总时长')
    progress = models.IntegerField(default=0, verbose_name='学习进度')
    is_favor = models.BooleanField(default=False, verbose_name='是否收藏')
    class Meta:
        db_table = 'my_course'
        verbose_name = '我的课程'
        verbose_name_plural = "我的课程"

# 评价表：
# id  用户id 课程id 内容（text） 星级（int）  用户头像 用户名
class Comment(BaseModel):
    """评价表"""
    user = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='用户',related_name='comments')
    course = models.ForeignKey("tcourse.Courses",on_delete=models.CASCADE, verbose_name='课程',related_name='comments')
    content = models.TextField(verbose_name='内容',default='')
    star = models.IntegerField(verbose_name='星级',default=5)
    avatar = models.CharField(max_length=300, verbose_name="头像", null=True, blank=True)
    username = models.CharField(max_length=50, verbose_name="用户名", null=True, blank=True)
    class Meta:
        db_table = 'comment'
        verbose_name = '评价'
        verbose_name_plural = "评价"
        ordering = ['-id']
    def save(self, *args, **kwargs):
        # 自动同步用户信息
        if self.user:
            self.username = self.user.username
            self.avatar = self.user.avatar
        super().save(*args, **kwargs)

# 申请退款记录表    一
# id  用户id  订单号  支付宝流水号 金额   状态
class Refund(BaseModel):
    """申请退款记录表"""
    user = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='用户',related_name='refund')
    order_no = models.CharField(max_length=100, verbose_name='订单号')
    alipay_number = models.CharField(max_length=100, verbose_name='支付宝流水号')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='金额')
    status = models.IntegerField(choices=[(0, '待处理'), (1, '已同意'), (2, '已拒绝'),(3,'已完成')], default=0, verbose_name='状态')
    class Meta:
        db_table = 'refund'
        verbose_name = '申请退款记录'
        verbose_name_plural = "申请退款记录"
        ordering = ['-id']
# 售后流程记录表（商家和系统）  多
# id   申请记录id   审批人   审批时间   状态（同意，不同意）订单号
class RefundProcess(BaseModel):
    """售后流程记录表"""
    refund = models.ForeignKey(Refund,on_delete=models.CASCADE, verbose_name='申请退款记录',related_name='refund_process')
    approver = models.CharField(max_length=32, verbose_name='审批人')
    approve_time = models.DateTimeField(verbose_name='审批时间')
    status = models.IntegerField(choices=[(1, '同意'), (2, '不同意')], default=1, verbose_name='状态')
    
    class Meta:
        db_table = 'refund_process'
        verbose_name = '售后流程记录'
        verbose_name_plural = "售后流程记录"
        ordering = ['-id']
    @property
    def order_no(self):
        return self.refund.order_no

# 充值活动表 
# id  充值金额   送金额  开始时间  结束时间   数量  领取数量
import datetime
class RechargeActivity(BaseModel):
    """充值活动表"""
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='充值金额')
    give_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='送金额')
    start_time = models.DateTimeField(default=datetime.datetime.now, verbose_name='开始时间')
    end_time = models.DateTimeField(default=datetime.datetime.now, verbose_name='结束时间')
    tcount = models.IntegerField(default=0, verbose_name='总数量')
    count = models.IntegerField(default=0, verbose_name='领取数量')
    class Meta:
        db_table = 'recharge_activity'
        verbose_name = '充值活动'
        verbose_name_plural = "充值活动"
        ordering = ['-id']

# 充值记录表
# id  用户id  金额  充值日期  支付方式  是否送   送金额  流水号
class RechargeRecord(BaseModel):
    """充值记录表"""
    user = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='用户',related_name='recharge_record')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='金额')
    recharge_date = models.DateTimeField(default=datetime.datetime.now, verbose_name='充值日期')
    pay_type = models.IntegerField(choices=[(1,'支付宝'),(2,'微信')], default=1, verbose_name='支付方式')
    is_give = models.BooleanField(default=False, verbose_name='是否送')
    give_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='送金额')
    recharge_no = models.CharField(max_length=100, verbose_name='流水号',default='')
    class Meta:
        db_table = 'recharge_record'
        verbose_name = '充值记录'
        verbose_name_plural = "充值记录"
        ordering = ['-id']






