from django.shortcuts import render
from hashlib import new
from rest_framework.response import Response
from rest_framework.views import APIView
import re,random,time,json
from tools.myredis import r
from tools.sms import sms
from tools.email_sender import my_send_mail
from .models import *
from .ser import *
from tools.pass_create import hash_password,check_password
from tools.myjwt import myjwt
from django.db.models import Q,F
from tools.common import get_alipay
from datetime import datetime

# 登录
class LoginView(APIView):
    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')
        type = request.data.get('type')
        if type == 'password': 
            user_info = User.objects.filter(username=username, is_delete=False).first()
            if not user_info:
                return Response({"code":400,"msg":"用户名不存在"})
            if not check_password(user_info.password,password):
                return Response({"code":400,"msg":"密码错误"})
        elif type == 'sms':
            phone = request.data.get('username')
            smsCode = request.data.get('smsCode')
            redis_code = r.get(phone)
            if not redis_code:
                return Response({"code":400,"msg":"手机号未发送验证码"})
            if smsCode != redis_code.decode():
                return Response({"code":400,"msg":"验证码错误"})
            user_info = User.objects.filter(phone=phone, is_delete=False).first()
            if not user_info:
                return Response({"code":400,"msg":"手机号不存在"})           
        # 生成token
        token = myjwt.encode({'user_id': user_info.id, 'username': user_info.username, 'phone': user_info.phone,'exp':int(time.time())+60*60*24 })
        return Response({"code":200, 'msg':'登录成功', 'token': token, 'user_id': user_info.id, 'username': user_info.username})

# 发送验证码
class SendSmsView(APIView):
    def post(self,request):
        phone = request.data.get('phone')
        if not re.match(r'^1[3456789]\d{9}$',phone):
            return Response({"code":400,"msg":"手机号格式错误"})
        # 判断redis中是否存在 
        code = r.get(phone)      
        if code: 
            return Response({"code":400,"msg":"手机号已发送验证码"})
        new_code = random.randint(1000,9999)
        res = sms.send_message(phone,new_code)
        if res:
            r.setex(phone,60,new_code)
            return Response({"code":200,'msg':'发送验证码成功'})
        else:
            return Response({"code":400,"msg":"发送验证码失败"})
      
# 注册
class RegisterView(APIView):
    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')
        phone = request.data.get('phone')
        code = request.data.get('code')
        
        # 检查用户名是否已存在
        if User.objects.filter(username=username, is_delete=False).exists():
            return Response({"code":400,"msg":"用户名已存在"})
        
        # 检查手机号是否已存在
        if User.objects.filter(phone=phone, is_delete=False).exists():
            return Response({"code":400,"msg":"手机号已被注册"})
        
        redis_code = r.get(phone)
        if not redis_code:
            return Response({"code":400,"msg":"手机号未发送验证码"})
        if code != redis_code.decode():
            return Response({"code":400,"msg":"验证码错误"})
        hashed_password = hash_password(password)
        try:
            user = User.objects.create(username=username,phone=phone,password=hashed_password)
            r.delete(phone)
            # 生成token
            token = myjwt.encode({'user_id': user.id,'username': user.username,'phone': user.phone})
            return Response({"code":200,'msg':'注册成功','token':token,'user_id': user.id})
        except Exception as e:
            return Response({"code":400,"msg":"注册失败，请稍后重试"})

# 发送邮箱验证码
class SendEmailView(APIView):
    def post(self,request):
        phone = request.data.get('phone')
        email = request.data.get('email')

        if not phone:
            return Response({"code":400,"msg":"请输入手机号"})
        if not email:
            return Response({"code":400,"msg":"请输入邮箱"})

        if not re.match(r'^1[3456789]\d{9}$', phone):
            return Response({"code":400,"msg":"手机号格式错误"})
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return Response({"code":400,"msg":"邮箱格式错误"})

        user = User.objects.filter(phone=phone, is_delete=False).first()
        if not user:
            return Response({"code":400,"msg":"用户不存在，请先注册"})

        user.email = email
        user.save()

        subject = "重置密码邮件"
        ecode = str(random.randint(1000,9999))
        reset_link = "http://localhost:5173/reset-password"
        message = f"""           
               密码重置请求
            您好，我们收到了您的密码重置请求。
            您的验证码是：{ecode} 
            您可以点击以下链接直接重置密码：
            {reset_link}
            该验证码将在10分钟后过期。
            如果您没有请求重置密码，请忽略此邮件。
            此邮件由系统自动发送，请勿回复。           
            """
        to_email = email
        res = my_send_mail.send(subject,message, to_email)
        if res:
            r.setex(ecode, 1800, phone)
            return Response({"code":200,'msg':'发送成功'})
        else:
            return Response({"code":400,"msg":"发送失败，请稍后重试","error":res})

# 重置密码
class ResetPasswordView(APIView):
    def post(self,request):
        code = request.data.get('code')
        passwd = request.data.get('passwd')
        repasswd = request.data.get('repasswd')

        if not code:
            return Response({"code":400,"msg":"请输入验证码"})
        if not passwd:
            return Response({"code":400,"msg":"请输入新密码"})
        if not repasswd:
            return Response({"code":400,"msg":"请输入确认密码"})
        if passwd != repasswd:
            return Response({"code":400,"msg":"两次输入的密码不一致"})

        if len(passwd) < 6:
            return Response({"code":400,"msg":"密码长度不能少于6位"})

        phone = r.get(code)
        if not phone:
            return Response({"code":400,"msg":"验证码已过期"})
        hashed_password = hash_password(passwd)
        user = User.objects.filter(phone=phone.decode(),is_delete=False).update(password=hashed_password)
        r.delete(code)
        return Response({"code":200,"msg":"重置成功"})

from tcourse.models import *
from tcourse.ser import *
#显示我的课程
class MyCourseView(APIView):
    def get(self,request):
        user_id = request.query_params.get('user_id')
        types = request.query_params.get('types')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        
        if not user_id:
            return Response({"code":400,"msg":"用户ID不能为空"})
        
        start = (page-1)*page_size
        end = start+page_size
        if int(types) == 3:
            mycourse = MyCourse.objects.filter(user_id=user_id,is_favor=True).all()[start:end]
        else:
            mycourse = MyCourse.objects.filter(user_id=user_id,status=int(types)).all()[start:end]
        ser = MyCourseSerializer(mycourse, many=True)
        return Response({"code":200,"msg":"查询成功","data":ser.data})

# 修改密码
# class UpdatePasswordView(APIView):
    def post(self,request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password:
            return Response({"code":400,"msg":"请输入当前密码"})
        if not new_password:
            return Response({"code":400,"msg":"请输入新密码"})
        if len(new_password) < 6:
            return Response({"code":400,"msg":"密码长度不能少于6位"})
        
        # 从请求头获取token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"code":400,"msg":"请先登录"})
        
        token = auth_header.split(' ')[1]
        try:
            payload = myjwt.decode(token)
            user_id = payload.get('user_id')
        except Exception as e:
            return Response({"code":400,"msg":"登录已过期，请重新登录"})
        
        # 获取用户信息
        user = User.objects.filter(id=user_id, is_delete=False).first()
        if not user:
            return Response({"code":400,"msg":"用户不存在"})
        
        # 验证旧密码
        if not check_password(user.password, old_password):
            return Response({"code":400,"msg":"当前密码错误"})
        
        # 更新密码
        hashed_password = hash_password(new_password)
        user.password = hashed_password
        user.save()      
        return Response({"code":200,"msg":"密码修改成功"})

# 获取我的订单接口:
# 参数 {"userid":,"status":,"page":,"page_size":}
# 请求方式：get
# 响应：{'code':200,'total':,'orderlist':[{'orderno':,'create_time':,'tmoney':,'details':[{},{}],'serverlist':[{},{}]}]}
class MyOrderView(APIView):
    def get(self,request):
        user_id = request.query_params.get('user_id')
        types = request.query_params.get('types')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 2))
        start = (page-1)*page_size
        end = start+page_size
        query = Q(user_id=user_id)
        if types:
            query &= Q(status=int(types))
        myorder = UserOrder.objects.filter(query).order_by('-create_time')[start:end]
        
        ser = UserOrderSerializer(myorder, many=True)
        return Response({"code":200,"msg":"查询成功","data":ser.data})

# 取消订单接口
class CancelOrderView(APIView):
    def post(self,request):
        orderno = request.data.get('orderno')
        if not orderno:
            return Response({"code":400,"msg":"请输入订单号"})
        order = UserOrder.objects.filter(order_number=orderno).first()
        if not order:
            return Response({"code":400,"msg":"订单不存在"})
        order.status = 5
        order.save()
        return Response({"code":200,"msg":"订单已取消"})

#添加评价接口
# 1、获取参数 用户id  课程id  内容  星级 用户头像 用户名
# 2、对数据验证，写入课程评价表
# 3、更新课程表中的总评价数字段
class CommentView(APIView):
    def post(self,request):
        user_id = request.data.get('user_id')
        course_id = request.data.get('course_id')
        content = request.data.get('content')
        star = request.data.get('star')
  
        if not user_id or not course_id or not content or not star:
            return Response({"code":400,"msg":"请输入评价信息"})
        
        # 获取用户信息
        user = User.objects.filter(id=user_id).first()       
        # 获取课程信息
        course = Courses.objects.filter(id=course_id).first()
        # 创建评论，同时保存用户的头像和用户名快照
        comment = Comment.objects.create(
            user_id=user_id,
            course_id=course_id,
            content=content,
            star=int(star),
            avatar=user.avatar if hasattr(user, 'avatar') else None,
            username=user.username,
        )
        
        course.total_comments += 1
        course.save()
        return Response({"code":200,"msg":"评价成功"})
# 详情页：获取此课程评价信息接口
# 1、获取参数 课程id
# 2、根据课程id查询课程评价表，按添加时间倒序，分页  （用户头像，用户名，内容，评价时间）
    def get(self,request):
        course_id = request.query_params.get('course_id')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        start = (page-1)*page_size
        end = start+page_size
        comment = Comment.objects.filter(course_id=course_id).order_by('-create_time').all()[start:end]
        ser = CommentSerializer(comment, many=True)
        return Response({"code":200,"msg":"查询成功","data":ser.data})
import requests      
from tools.common import get_alipay
# 申请退款接口
class RefundView(APIView):
    def post(self,request):
        user_id = request.data.get('user_id')
        orderno = request.data.get('orderno')
        if not orderno or not user_id:
            return Response({"code":400,"msg":"参数错误"})
        order = UserOrder.objects.filter(order_number=orderno).first()
        if not order:
            return Response({"code":400,"msg":"订单不存在"})
        # 检查订单状态 是否允许退款  
        if int(order.status) not in [2,3,4]:
            return Response({"code":400,"msg":"订单状态错误"})
       
        refund = Refund.objects.create(user_id=user_id,order_no=orderno,
        alipay_number=order.transaction_no,amount=order.actual_payment,status=0)
        order.status = 6
        order.save()
        
        # 调用支付宝退款接口
        try:
            alipay = get_alipay()
            query_params = alipay.refund(out_trade_no=str(orderno), refund_amount=float(order.actual_payment))
            pay_url = "https://openapi-sandbox.dl.alipaydev.com/gateway.do?{0}".format(query_params)
            mes = requests.get(pay_url, timeout=30)
            data = json.loads(mes.text)
            
            if data.get('alipay_trade_refund_response', {}).get('code') == '10000':
                order.status = 7
                order.save()
                refund.status = 3
                refund.save()
                details = order.details.all()
                for i in details:
                    MyCourse.objects.filter(course_id=i.course, user_id=order.user_id).update(status=4)
                return Response({"code":200,"msg":"退款成功"})
            else:
                error_msg = data.get('alipay_trade_refund_response', {}).get('msg', '退款失败')
                return Response({"code":400,"msg":error_msg})
        except Exception as e:
            # 如果支付宝退款失败，记录日志并返回错误
            print(f"支付宝退款失败: {str(e)}")
            return Response({"code":400,"msg":"退款失败，请稍后重试"})
    def get(self,request):
        user_id = request.query_params.get('user_id')
        refund = Refund.objects.filter(user_id=user_id).all()
        ser = RefundSerializer(refund, many=True)
        return Response({"code":200,"msg":"查询成功","data":ser.data})

# 充值活动查询接口
class RechargeActivityView(APIView):
    def get(self, request):
        amount = request.query_params.get('amount')
        if not amount:
            return Response({"code": 400, "msg": "参数错误"})
        now = datetime.now()
        activity = RechargeActivity.objects.filter(
            amount__lte=float(amount),
            start_time__lte=now,
            end_time__gte=now
        ).first()
        if activity and int(activity.tcount) - int(activity.count) > 0:

            return Response({"code": 200, "msg": "查询成功", "data": {
                "id": activity.id,
                "amount": float(activity.amount),
                "give_amount": float(activity.give_amount),
                "start_time": activity.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                "end_time": activity.end_time.strftime('%Y-%m-%d %H:%M:%S')
            }})
        else:
            return Response({"code": 200, "msg": "暂无优惠活动", "data": None})

# 充值接口
# (1)获取参数  用户id 充值金额  支付方式
# 
# (3)是否有优惠，如果有  金额=充值金额+优惠
# (4)写入充值记录表  流水号为空
# (5) 根据支付类型调用支付宝充值  调用pay接口
class RechargeView(APIView):
    def post(self,request):
        user_id = request.data.get('user_id')
        amount = request.data.get('amount')
        pay_type = request.data.get('pay_type')
        if not user_id or not amount or not pay_type:
            return Response({"code":400,"msg":"参数错误"})
        # (2)根据充值金额充值活动表中查询符合条件的记录  充值金额大于表中的总金额  充值日期大于开始时间  小于结束时间  领取数量小于总数量 
        now = datetime.now() 
        is_give = False
        give_amount = 0
        activity = RechargeActivity.objects.filter(amount__lte=float(amount),start_time__lte=now,end_time__gte=now).first()
        if activity:
            if int(activity.tcount) - int(activity.count) > 0:
                is_give = True
                give_amount = activity.give_amount
                
        record = RechargeRecord.objects.create(
            user_id=user_id,
            amount=float(amount),
            recharge_date=now,
            pay_type=pay_type,
            is_give=is_give,
            give_amount=give_amount,
            recharge_no='',
        )
        if activity:
            activity.count = int(activity.count)+1
            activity.save()
        orderno = str(record.id) + 'a'
        if int(pay_type) == 1:           
            alipay = get_alipay()
            query_params = alipay.direct_pay(
                out_trade_no=str(orderno),
                subject="课程充值",
                total_amount=float(amount),
            )
            pay_url = "https://openapi-sandbox.dl.alipaydev.com/gateway.do?{0}" .format(query_params)
            print(pay_url)
            return Response({"code": 200, "msg": "支付成功","pay_url":pay_url})

#获取用户信息
class UserInfo(APIView):
    def get(self, request):
        user_id = request.query_params.get("user_id")
        userinfo = User.objects.filter(id=user_id).first()
        ser = UserSerializer(userinfo, many=False)
        return Response({"code": 200, "msg": "查询成功", "data": ser.data}) 


        
                
            
