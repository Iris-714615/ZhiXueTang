from django.db import models
from tools.models import BaseModel


# Create your models here.

#id 名称 父id 级别 图片 是否推荐
class Category(BaseModel):
    name = models.CharField(max_length=50, verbose_name='名称')
    pid = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='父分类', null=True, blank=True)
    level = models.IntegerField(verbose_name='级别',default=1)
    image = models.ImageField(upload_to='upload/category/', verbose_name='图片')
    is_recommend = models.BooleanField(verbose_name='是否推荐',default=True)
    floor = models.IntegerField(verbose_name='楼层',default=0)
    top_category = models.IntegerField(verbose_name='顶级分类',default=0)
    class Meta:
        db_table = 'category'
        verbose_name = '课程分类'
        verbose_name_plural = "课程分类"
    def __str__(self):
        return self.name

class Navcate(BaseModel):
    name = models.CharField(max_length=50, verbose_name='名称')
    url = models.CharField(max_length=200, verbose_name='链接')
    weight = models.IntegerField(verbose_name='权重',default=0)

    class Meta:
        db_table = 'nav_cate'
        verbose_name = '导航栏'
        verbose_name_plural = "导航栏"
    def __str__(self):
        return self.name

#焦点图表

#id  图片地址  跳转链接  权重   是否展示
class Banner(BaseModel):
    image = models.ImageField(upload_to='upload/banner/', verbose_name='图片')
    url = models.CharField(max_length=200, verbose_name='跳转链接')
    weight = models.IntegerField(verbose_name='权重',default=0)
    is_show = models.BooleanField(verbose_name='是否展示',default=True)
    class Meta:
        db_table = 'banner'
        verbose_name = '焦点图表'
        verbose_name_plural = "焦点图表"
    def __str__(self):
        return self.title

# 标签表
# id   名称(title)  图像()  介绍  是否首页推荐  是否上线  权重
class Tags(BaseModel):
    title = models.CharField(max_length=50, verbose_name='名称')
    image = models.ImageField(upload_to='upload/tag/', verbose_name='图片')
    description = models.CharField(max_length=200, verbose_name='介绍')
    is_recommend = models.BooleanField(verbose_name='是否首页推荐',default=True)
    is_online = models.BooleanField(verbose_name='是否上线',default=True)
    weight = models.IntegerField(verbose_name='权重',default=0)
    
    class Meta:
        db_table = 'tag'
        verbose_name = '标签表'
        verbose_name_plural = "标签表"
    def __str__(self):
        return self.title


# 讲师表
# id   头像  姓名  职称  简介
class Teacher(BaseModel):
    ROLE_CHOICES = (
        (0,'讲师'),
        (1,'导师'),
        (2,'班主任')
    )
    avatar = models.ImageField(upload_to='upload/teacher/', verbose_name='图片')
    role = models.IntegerField(verbose_name='角色',choices=ROLE_CHOICES,default=0)
    name = models.CharField(max_length=50, verbose_name='姓名')
    title = models.CharField(max_length=50, verbose_name='职称')
    description = models.CharField(max_length=200, verbose_name='介绍')
    class Meta:
        db_table = 'teacher'
        verbose_name = '讲师表'
        verbose_name_plural = "讲师表"
    def __str__(self):
        return self.name

# 课程表

# id   名称  图标   课程简介   级别(初级，中级，高级)    销量   价格  优惠价格  **所属分类**(外键)   顶级分类（int）    **楼层  （默认0）**   图标(新课，升级，会员)

class Courses(BaseModel):
    title = models.CharField(max_length=50, verbose_name='名称')
    image = models.ImageField(upload_to='upload/course/', verbose_name='图片')
    description = models.CharField(max_length=200, verbose_name='课程简介')
    level = models.IntegerField(verbose_name='级别',choices=[(1,'初级'),(2,'中级'),(3,'高级')],default=1)
    studentCount = models.IntegerField(verbose_name='课程学习人数',default=0)
    price = models.FloatField(verbose_name='价格',default=0.0)
    discount = models.FloatField(verbose_name='优惠价格',default=0.0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='所属分类')
    top_category = models.IntegerField(verbose_name='顶级分类',default=0)
    floor = models.IntegerField(verbose_name='楼层',default=0)
    is_recommend = models.BooleanField(verbose_name='是否首页推荐',default=True)
    tags = models.ManyToManyField(Tags, verbose_name='标签',related_name='courses')
    click_count = models.IntegerField(verbose_name='点击量',default=10)
    is_free = models.BooleanField(verbose_name='课程付费类型',default=False)

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='讲师',default=0)
    lessons = models.IntegerField(verbose_name='课程课时数',default=0)
    pub_lessons = models.IntegerField(verbose_name='课程已更新课时数',default=0)
    status = models.IntegerField(verbose_name='课程状态',choices=[(0,'预上线'),(1,'上线'),(2,'下线')],default=1)
    attachment_path = models.CharField(max_length=300, verbose_name='课程附件路径',null=True, blank=True)
    introduction = models.TextField(verbose_name="课程介绍", null=True, blank=True)
    outcomes = models.TextField(verbose_name="课程收获", null=True, blank=True)
    audience = models.TextField(verbose_name="适合人群", null=True, blank=True)
    total_comments = models.IntegerField(verbose_name='总评价数',default=0)
    class Meta:
        db_table = 'courses'
        verbose_name = '课程表'
        verbose_name_plural = "课程表"
    def __str__(self):
        return self.title

# 章
# id   名称  课时数  课程(外键)
class Chapter(BaseModel):
    title = models.CharField(max_length=50, verbose_name='名称')
    number = models.IntegerField(verbose_name='章节序号',default=1)
    summary = models.CharField(max_length=200, verbose_name='章节简介')
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name='课程',related_name='chapter')   
    weight = models.IntegerField(verbose_name='权重',default=1)
    class Meta:
        db_table = 'chapter'
        verbose_name = '章表'
        verbose_name_plural = "章表"
    def __str__(self):
        return self.title
# 节
# id   名称  时长  视频地址    是否免费  章(外键)
class Lesson(BaseModel):
    title = models.CharField(max_length=50, verbose_name='名称')
    orders = models.IntegerField(verbose_name='节序号',default=1)
    duration = models.IntegerField(verbose_name='时长',default=0)
    link = models.CharField(max_length=200, verbose_name='视频地址')
    is_free_trial = models.BooleanField(verbose_name='是否免费',default=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, verbose_name='章',default=1,related_name='lesson')
    class Meta:
        db_table = 'lesson'
        verbose_name = '节表'
        verbose_name_plural = "节表"
    def __str__(self):
        return self.title
#课程价格表
class CoursePrice(BaseModel):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name='prices')
    types = models.IntegerField(verbose_name='价格类型',default=1,choices=[(1,'永久有效'),(2,'一个月'),(3,'一年'),(4,'2年')])
    name = models.CharField(max_length=50, verbose_name='价格名称')
    price = models.DecimalField(verbose_name='价格',max_digits=10,decimal_places=2,default=0.00)
    class Meta:
        db_table = 'course_price'
        verbose_name = '课程价格表'
        verbose_name_plural = "课程价格表"
# 优惠券表 id 名称 满 减  开始时间 结束时间 状态(0-未使用，1-已使用，2-已过期)
class Coupon(BaseModel):
    name = models.CharField(max_length=50, verbose_name='名称')
    full = models.IntegerField(verbose_name='满金额',default=0)
    minus = models.IntegerField(verbose_name='减金额',default=0)
    start_time = models.DateField(verbose_name='开始时间')
    end_time = models.DateField(verbose_name='结束时间')
    class Meta:
        verbose_name = '优惠券'
        db_table = 'coupon'
    def __str__(self):
        return self.name

#订单表
# id  订单号（唯一）  用户id   订单状态    下单时间   是否使用优惠券     优惠编号   优惠金额   实际支付金额  支付方式   流水号
class UserOrder(BaseModel):
    order_number = models.CharField(max_length=50, verbose_name='订单号',unique=True)
    user = models.ForeignKey('euser.User', on_delete=models.CASCADE, verbose_name='用户')
    status = models.IntegerField(verbose_name='订单状态',choices=[(1,'待支付'),(2,'已支付'),
    (3,'已评价'),(4,'已完成'),(5,'已取消'),(6,'退款中'),(7,'已退款')],default=1)
    total_amount = models.DecimalField(verbose_name='订单总金额',max_digits=10,decimal_places=2,default=0.00)
    payment_method = models.IntegerField(verbose_name='支付方式',default=0)
    is_use_coupon = models.BooleanField(verbose_name='是否使用优惠券',default=False)
    coupon_number = models .CharField(max_length=50, verbose_name='优惠券编号',null=True, blank=True,default='')
    coupon_amount = models.DecimalField(verbose_name='优惠金额',max_digits=10,decimal_places=2,default=0.00)
    actual_payment = models.DecimalField(verbose_name='实际支付金额',max_digits=10,decimal_places=2,default=0.00)
    transaction_no = models.CharField(max_length=200, verbose_name='流水号',null=True, blank=True,default='')
    class Meta:
        db_table = 'user_order'
        verbose_name = '订单表'
        verbose_name_plural = "订单表"
    def __str__(self):
        return self.order_number

# id   订单号（外键关联订单表） 课程id  图片  价格 介绍  有效期类型  用户id
class OrderDetail(BaseModel):
    # 外键关联订单表指定字段order_number
    # 外键关联课程表
    order = models.ForeignKey(UserOrder, on_delete=models.CASCADE, verbose_name='订单',to_field='order_number',related_name='details')
    course = models.IntegerField(verbose_name='课程id')
    price = models.DecimalField(verbose_name='价格',max_digits=10,decimal_places=2,default=0.00)
    introduction = models.CharField(max_length=200, verbose_name="课程介绍",default='')
    valid_type = models.IntegerField(verbose_name='有效期类型',default=0)
    user = models.ForeignKey('euser.User', on_delete=models.CASCADE, verbose_name='用户',related_name='details')
    class Meta:
        db_table = 'order_detail'
        verbose_name = '订单详情表'
        verbose_name_plural = "订单详情表"
   
