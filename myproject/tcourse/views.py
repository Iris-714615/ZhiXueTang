from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .ser import *
from .models import *
from tools.myredis import r
import json
from django.db.models import Q,F
from datetime import datetime, timedelta, date
from euser.models import *
#from .wxpay import WxPayConfig

#获取分类接口
class CategoryView(APIView):
    def get(self,request):
        # clist = r.get("categorylist")
        # if clist:
        #     return Response({"code":200,"msg":"success","data":json.loads(clist)})

        # if r.setnx("catelock",1):
        #     r.expire("catelock",5)
        category = Category.objects.filter(is_delete=False,is_recommend=True,level=1).all()
        ser = CategorySerializer(category, many=True)
        data = ser.data
            # r.setex("categorylist",json.dumps(data),60)
            # r.delete("catelock")
        return Response({"code":200,"msg":"success","data":data})

        # else:
        #     sleep(1)
        #     clist = r.get("categorylist")
        #     if clist:
        #         return Response({"code":200,"msg":"success","data":json.loads(clist)})
        #     return Response({"code":500,"msg":"error","data":[]})

#获取导航分类接口
class NavcateView(APIView):
    def get(self,request):
        try:
            nlist = r.get("navlist")
            if nlist:
                return Response({"code":200,"msg":"success","data":json.loads(nlist)})
        except Exception as e:
            pass
        
        navcate = Navcate.objects.filter(is_delete=False).order_by('weight').all()
        ser = NavcateSerializer(navcate, many=True)
        data = ser.data
        try:
            r.set("navlist",json.dumps(data))
        except Exception as e:
            pass
        return Response({"code":200,"msg":"success","data":data})

#获取banner接口
class BannerView(APIView):
    def get(self,request):
        # 暂时禁用缓存，排查数据问题
        # blist = r.get("bannerlist")
        # if blist:
        #     return Response({"code":200,"msg":"success","data":json.loads(blist)})
        
        banner = Banner.objects.filter(is_delete=False,is_show=True).order_by('weight').all()
        print(f"查询到的Banner数量: {len(banner)}")  # 添加调试信息
        ser = BannerSerializer(banner, many=True)
        data = ser.data
        # r.set("bannerlist",json.dumps(data))
        return Response({"code":200,"msg":"success","data":data})

#获取标签接口
class TagsView(APIView):
    def get(self,request):
        tags = Tags.objects.filter(is_delete=False,is_online=True,is_recommend=True).all()
        ser = TagsSerializer(tags, many=True)
        return Response({"code":200,"msg":"success","data":ser.data})

#获取推荐分类接口
class RecommendCate(APIView):
    def get(self,request):
        floor = request.GET.get("floor")
        if not floor:
            return Response({"code":400,"msg":"error"})
        recate = Category.objects.filter(is_delete=False,is_recommend=True,level=1,floor=floor).all()
        ser = CategorySerializer(recate, many=True)
        return Response({"code":200,"msg":"success","data":ser.data})

#获取课程列表接口
class CoursesView(APIView):
    def get(self,request):
        floor = request.GET.get("floor")
        category = request.GET.get("category")
        if not category or not floor:
            return Response({"code":400,"msg":"error"})
        courses = Courses.objects.filter(is_delete=False,is_recommend=True,floor=floor,top_category=category).all()
        ser = CoursesSerializer(courses, many=True)
        return Response({"code":200,"msg":"success","data":ser.data})

#获取所有一级分类接口
class AllCategoryView(APIView):
    def get(self,request):
        category = Category.objects.filter(is_delete=False,is_recommend=True,level=1).all()
        ser = Cate1Serializer(category, many=True)
        return Response({"code":200,"msg":"success","data":ser.data})

#获取所有课程接口
class AllCoursesView(APIView):
    def get(self,request):
        top_category = request.GET.get("top_category")
        order = request.GET.get("order")
        feetype = request.GET.get("feetype")
        page = request.GET.get("page", "1")
        page_size = request.GET.get("page_size", "10")
        query = Q(is_delete=False,is_recommend=True)
        if top_category and top_category != "all":
            query &= Q(top_category=top_category)
        if feetype == "all":
            query &= Q(is_free=True)|Q(is_free=False)
        else:
            query &= Q(is_free=feetype)
        order_type = "-studentCount"
        if order:
            order_type = order
        start = (int(page)-1)*int(page_size)
        end = int(page)*int(page_size)
        courses = Courses.objects.filter(query).order_by(order_type).all()[start:end]
        count = Courses.objects.filter(query).count()
       
        ser = CoursesSerializer(courses, many=True) 
        return Response({"code":200,"msg":"success","data":ser.data,"count":count})

class TestView(APIView):
    def get(self,request):
        # 调用微信支付
            client = WxPayClient()
            total_fee = 100  # 单位是分
            description = f"码境空间课程订单:{234234324234}"
            code_url = client.create_order(f"234234324234", total_fee, description)
            if not code_url:
                return Response({"code": 0, "message": "微信下单失败"})
            return Response({"code":200,"msg":"success","code_url":code_url})
#获取课程详情接口
class CourseDetailView(APIView):
    def get(self,request,pk):
        id = pk
        course = Courses.objects.filter(id=id,is_delete=False).first()
        if not course:
            return Response({"code":400,"msg":"error"})
        ser = CourseDetailSerializer(course)
        return Response({"code":200,"msg":"success","data":ser.data})

#加入购物车接口
class CartView(APIView):
    """加入购物车"""
    def post(self, request):
        userid = request.data.get('user_id')
        courseid = request.data.get('courseid')
        
        if not courseid or not userid:
            return Response({"code": 400, "msg": "error"})      
        # 验证课程是否存在且有效
        course = Courses.objects.filter(id=courseid, is_delete=False, status=1).first()
        print(course)
        if not course:
            return Response({"code": 400, "msg": "课程不存在或已下线"})       
         
        # 检查购物车中是否已存在该课程
        if r.hexists(f"carts{userid}", courseid):
            return Response({"code": 400, "msg": "课程已在购物车中"}) 
        pricelist = [{'types':c.types,'name':c.name,'price':str(c.price)} for c in course.prices.all()]     
        # 构建购物车商品数据
        cart_item = json.dumps({
            "id": courseid,
            "is_check": 1,
            "image": str(course.image.url) if course.image else "",
            "title": course.title,
            "type": 1,
            "price": pricelist[0]['price'],           
            "pricelist": pricelist,
        })
        # 存入Redis Hash结构
        r.hset(f"carts{userid}", courseid, cart_item)      
        # 设置过期时间 24小时
        # r.expire(f"carts{userid}", 3600)      
        return Response({"code": 200, "msg": "加入购物车成功"})
    """查询购物车商品"""
    def get(self,request):
        userid = request.GET.get("user_id")
        if not userid:
            return Response({"code": 400, "msg": "error"})               
        cart = r.hgetall(f"carts{userid}")
        cartlist = []
        # 检查 cart 是否是字典类型，避免布尔值错误
        if isinstance(cart, dict):
            for key,value in cart.items():
                try:
                    cartlist.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    continue
        return Response({"code":200,"msg":"success","data":cartlist})

#删除购物车商品接口
class CartDeleteView(APIView):
    """删除购物车商品"""
    def post(self, request):
        user_id = request.data.get('user_id')
        courseids = request.data.get('courseids')
        if not courseids or not user_id:
            return Response({"code": 400, "msg": "请选择要删除的商品"})
        if type(courseids) == list:
            r.hdelall(f"carts{user_id}", *courseids)
        else:
            r.hdel(f"carts{user_id}", courseids)
        return Response({"code": 200, "msg": "删除成功"})

#全选/取消全选接口
class CartSelectView(APIView):
    """全选/取消全选"""
    def post(self, request):
        user_id = request.data.get('user_id')
        is_check = request.data.get('is_check',1)      
        cart = r.hgetall(f"carts{user_id}")
        if isinstance(cart, dict):
            for key,value in cart.items():
                try:
                    course = json.loads(value)
                    course['is_check'] = is_check
                    r.hset(f"carts{user_id}",key, json.dumps(course))
                except (json.JSONDecodeError, TypeError):
                    continue
        return Response({"code": 200, "msg": "操作成功"})

#切换商品选中状态接口
class CartToggleView(APIView):
    """切换商品选中状态"""
    def post(self, request):
        user_id = request.data.get('user_id')
        courseids = request.data.get('courseids')
        if not courseids or not user_id:
            return Response({"code": 400, "msg": "error"})
        value = r.hget(f"carts{user_id}", courseids)
        if not value or value is False:
            return Response({"code": 400, "msg": "商品不在购物车中"})
        try:
            course = json.loads(value)
            if course['is_check'] == 1:
                course['is_check'] = 0
            else:
                course['is_check'] = 1
            r.hset(f"carts{user_id}", courseids, json.dumps(course))     
            return Response({"code": 200, "msg": "操作成功"})
        except (json.JSONDecodeError, TypeError, KeyError):
            return Response({"code": 400, "msg": "购物车数据损坏"})

#更新商品有效期接口
class CartUpdateValidityView(APIView):
    """更新商品有效期"""
    def post(self, request):
        user_id = request.data.get('user_id')
        courseid = request.data.get('courseid')
        type_val = request.data.get('type')     
        if not courseid or not user_id or type_val is None:
            return Response({"code": 400, "msg": "error"})      
        value = r.hget(f"carts{user_id}", courseid)
        if not value or value is False:
            return Response({"code": 400, "msg": "商品不在购物车中"})    
        try:
            course = json.loads(value)
            for item in course['pricelist']:
                if int(item['types']) == int(type_val):
                    course['price'] = item['price']
                    course['type'] = int(type_val)
                    break
            r.hset(f"carts{user_id}", courseid, json.dumps(course))
            return Response({"code": 200, "msg": "更新成功"})
        except (json.JSONDecodeError, TypeError, KeyError):
            return Response({"code": 400, "msg": "购物车数据损坏"})

# 获取用户选中购物车的接口
class MyCartView(APIView):
    """获取用户选中购物车的商品"""
    def get(self, request):
        user_id = request.GET.get("user_id")
        if not user_id:
            return Response({"code": 400, "msg": "error"})               
        cart = r.hgetall(f"carts{user_id}")
        cartlist = [] 
        total_price = 0
        if isinstance(cart, dict):
            for key,value in cart.items():
                try:
                    course = json.loads(value)
                    if course['is_check'] == 1:
                        expname = ""
                        for i in course['pricelist']:
                            if  int(course['type']) == int(i['types']):
                                expname = i['name']
                                break                               
                        cartlist.append({
                            "id": course['id'],
                            "is_check": course['is_check'],
                            "image": str(course['image']),
                            "title": course['title'],
                            "type": course['type'],
                            "price": course['price'],
                            "expname": expname,                            
                        })
                        total_price += float(course['price'])
                except (json.JSONDecodeError, TypeError, KeyError):
                    continue
        return Response({"code":200,"msg":"success","data":cartlist,"total_price":total_price})

#获取满足条件的优惠券的接口
class CouponView(APIView):
    """获取满足条件的优惠券"""
    def get(self, request):
        tmoney = request.query_params.get("tmoney")
        if not tmoney:
            return Response({"code": 400, "msg": "error"}) 
        # 查询优惠券表中满足条件的记录
        now = date.today()
        couponlist = Coupon.objects.filter(is_delete=False, full__lte=float(tmoney), start_time__lte=now, end_time__gte=now).all()
        print(f"查询到的优惠券数量: {len(couponlist)}")  # 添加调试日志
        ser = CouponSerializer(couponlist,many=True)
        return Response({"code":200,"msg":"success","data":ser.data}) 

# 生成订单接口
import random
from tools.sf import next_snowflake_id
from django.db import transaction
class OrdersView(APIView):
    """生成订单"""
    def get(self,request):
        order_number = request.query_params.get("order_number")
        if not order_number:
            return Response({"code": 400, "msg": "error"})
        orders = UserOrder.objects.filter(order_number=order_number).first()
        details = orders.details.all()
        detail_list = []
        for detail in details:
            course = Courses.objects.filter(id=detail.course).first()
            expire_text_map = {
                1: '永久有效',
                2: '1个月',
                3: '1年',
                4: '2年'
            }
            expire_time = ""
            if detail.valid_type == 1:
                expire_text = expire_text_map.get(1, '永久有效')
                expire_time = ""
            elif detail.valid_type == 2:
                expire_text = expire_text_map.get(2, '1个月')
                expire_time = (orders.create_time + timedelta(days=30)).strftime("%Y-%m-%d") if orders.create_time else ""
            elif detail.valid_type == 3:
                expire_text = expire_text_map.get(3, '1年')
                expire_time = (orders.create_time + timedelta(days=365)).strftime("%Y-%m-%d") if orders.create_time else ""
            elif detail.valid_type == 4:
                expire_text = expire_text_map.get(4, '2年')
                expire_time = (orders.create_time + timedelta(days=730)).strftime("%Y-%m-%d") if orders.create_time else ""
            else:
                expire_text = '永久有效'
                expire_time = ""
            detail_data = {
                "id": detail.id,
                "course_id": detail.course,
                "course": {
                    "id": course.id,
                    "name": course.title,
                    "course_img": course.image.url if course.image else "",
                    "brief": course.description,
                    "teacher": {
                        "name": course.teacher.name if course.teacher else ""
                    }
                },
                "price": detail.price,
                "expire_text": expire_text,
                "expire_time": expire_time
            }
            detail_list.append(detail_data)
        return Response({"code": 200,"msg":"success","orders":{"pay_time":"2026-05-09","tmoney":orders.actual_payment,"order_details":detail_list,"order_number":order_number}})
    def post(self, request):
        user_id = request.data.get('user_id')
        couponid = request.data.get('couponid')
        pay_type = request.data.get('pay_type')
        if not pay_type or not user_id :
            return Response({"code": 400, "msg": "error"})
        if r.setnxex(f"lock{user_id}",1):   
            # orderno = random.randint(1000000,9999999)
            orderno = next_snowflake_id()
            print(orderno)
            is_coupon = False
            coupon_amount = 0.00
            coupon_number = 0
            if couponid and str(couponid).strip() and int(couponid) > 0:
                is_coupon = True
                coupon = Coupon.objects.filter(id=int(couponid)).first()
                coupon_amount = coupon.minus
                coupon_number = couponid
            with transaction.atomic():
                orders = UserOrder.objects.create(order_number=orderno,user_id=user_id,
                status=1,payment_method=pay_type,total_amount=0,is_use_coupon=is_coupon,
                coupon_number=coupon_number,coupon_amount=coupon_amount,actual_payment=0.00)
                # 生成订单详情
                # 2.根据userid获取选中的购物车数据，计算总金额
                cartlist = r.hgetall(f"carts{user_id}")
                total_price = 0
                if isinstance(cartlist, dict):
                    for key,value in cartlist.items():
                        try:
                            course = json.loads(value)
                            if course['is_check'] == 1:
                                total_price += float(course['price'])
                                #写入订单详情表
                                OrderDetail.objects.create(
                                    order = orders,
                                    introduction="课程介绍",
                                    valid_type=int(course['type']),
                                    course=course['id'],
                                    price=course['price'],
                                    user_id=user_id,
                                )
                                #删除购物车
                                r.hdel(f"carts{user_id}",key)
                        except (json.JSONDecodeError, TypeError, KeyError):
                            continue

                orders.total_amount = total_price
                orders.actual_payment = float(total_price) - float(coupon_amount)       
                orders.save()
                r.delete(f"lock{user_id}")
                #调用订单延时任务
                cancel_order.apply_async(args=[orderno],countdown=300)
                #把订单号存入redis list
                r.lpush("cancelorder",orderno)
                return Response({"code": 200, "msg" : "生成订单成功","orderno":str(orderno)})

        else:
            return Response({"code": 400, "msg": "订单生成失败"})
       
    
from tools.common import get_alipay
class PayView(APIView):
    """支付"""
    def post(self, request):
        orderno = request.data.get('orderno')
        if not orderno:
            return Response({"code": 400, "msg": "error1"})
        orders = UserOrder.objects.filter(order_number=str(orderno)).first()
        if not orders:
            return Response({"code": 400, "msg": "error"})
        alipay = get_alipay()
        query_params = alipay.direct_pay(
            out_trade_no=str(orderno),
            subject="课程购买",
            total_amount=float(orders.actual_payment),
        )
        pay_url = "https://openapi-sandbox.dl.alipaydev.com/gateway.do?{0}" .format(query_params)

        return Response({"code": 200, "msg": "支付成功","pay_url":pay_url})


from django.http import HttpResponseRedirect
from urllib.parse import unquote, parse_qs
from euser.models import MyCourse
# 支付宝回调接口
class AliPayCallbackView(APIView):
    """支付宝回调"""
    def get(self, request):
        alipay = get_alipay()
        data = request.GET
        # datames = request.GET.dict()
        # 获取原始的查询字符串
        query_string = request.META.get('QUERY_STRING', '')
        
        # 从原始查询字符串中正确提取签名
        parsed_query = parse_qs(query_string)
        sign = parsed_query.get('sign', [None])[0]
        if sign:
            # 先 unquote，然后把空格换回 +
            sign = unquote(sign)
            sign = sign.replace(' ', '+')
        
        # 构建验签数据
        datames = {k:v for k,v in data.items()}
        if 'sign' in datames:
            datames.pop('sign')       
        if not sign:
            return HttpResponseRedirect("http://localhost:5173/error")
        flag = alipay.verify(datames, sign)
        if not flag:
            return HttpResponseRedirect("http://localhost:5173/error")
        orderno = datames['out_trade_no']
        transtion_no = datames['trade_no']
        if 'a' in orderno:
            #充值订单
            record_id = orderno.replace('a', '')
            record = RechargeRecord.objects.filter(id=record_id).first()
            if record:
                record.recharge_no = transtion_no
                record.save()
                # 更新用户账户余额
                User.objects.filter(id=record.user_id).update(account=F('account') + record.amount + record.give_amount)
            return HttpResponseRedirect("http://localhost:5173/user")
        else:
            #支付订单
            
            userorder = UserOrder.objects.filter(order_number=orderno).first()
            if not userorder:
                return Response({"code": 400, "msg": "error"})
            userorder.status = 2
            userorder.transaction_no = transtion_no
            userorder.save()
            # 写入我的课程表 用户id 课程id 类型 开始时间 结束时间
            r.lrem("cancelorder",0,orderno)
            # send_smscode.delay("17760476758",f"支付成功，订单号为：{orderno}")

            orserdetail = userorder.details.all()
            print(orserdetail)
            for i in orserdetail:
                stime = datetime.datetime.now()
                endtime = stime + timedelta(days=30)
                if i.valid_type == 1:
                    stime = None
                    endtime = None
                elif i.valid_type == 3:
                    endtime = stime + timedelta(days=365)
                elif i.valid_type == 4:
                    endtime = stime + timedelta(days=730)
                MyCourse.objects.create(
                    user_id=userorder.user_id,
                    course_id=i.course,
                    course_type=i.valid_type,
                    start_time=stime,
                    end_time=endtime,
                )
            
            return HttpResponseRedirect("http://localhost:5173/paysuccess?orderno="+ str(orderno))

from tasks.tasks import cancel_order,send_smscode
class TestCeleryView(APIView):
    def get(self,request):
        #异步任务
        send_smscode.delay("18567311174","1112")
        #延时任务
        cancel_order.apply_async(args=["123456"], countdown=30)
        return Response({"code": 200, "msg": "延时任务已提交，30秒后执行"})

       
        
from elasticsearch import Elasticsearch
es = Elasticsearch(hosts=["http://localhost:9200"])
class SearchView(APIView):
    def get(self,request): 
        name = request.GET.get("name")
        page = request.GET.get("page",1)
        size = request.GET.get("size",2)
        start = (int(page)-1)*int(size)      
        
        if not es.indices.exists(index="courses"):
            return Response({"code": 400, "msg": "搜索索引未初始化，请先调用POST接口初始化数据"})
        
        search = {
            "query":{
                "match":{
                    "name":name
                },
                "from":start,
                "size":int(size),
                "_source":["id","name","types"],
                "sort":{"id":{"order":"desc"}}}}    
        if not name:
            search= {"query":{"match_all":{}},"from":start,
                "size":int(size),
                "_source":["id","name","types"],
                "sort":{"id":{"order":"desc"}}}
        res = es.search(index="courses", body=search)
        total = res["hits"]["total"]["value"]
        list = res["hits"]["hits"]
        data = []
        for i in list:
            data.append(i["_source"])
        return Response({"code": 200, "msg": "success",'total':total,"data":data})
    
    def post(self,request):
        if es.indices.exists(index="courses"):
            es.indices.delete(index="courses")
        
        course = Courses.objects.filter(is_delete=False).all()
        for i in course:
            es.index(index="courses", body={"id":i.id,"name":i.title,"table_name":"courses","types":"course"})
        comment = Comment.objects.filter(is_delete=False).all()
        print(f"查询到的评论数量: {len(comment)}")
        for i in comment:
            print(f"评论ID: {i.id}, 内容: {i.content[:20]}...")
            es.index(index="courses", body={"id":i.id,"name":i.content,"table_name":"comment","types":"comment"})
        res = es.search(index="courses", body={"query":{"match_all":{}}})
        return Response({"code": 200,"msg": "操作成功","res":res})
