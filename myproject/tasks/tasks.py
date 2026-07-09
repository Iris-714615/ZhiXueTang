# 现在我将创建tasks/tasks.py文件，定义两个定时任务：
# 1. print_current_time - 每分钟打印当前时间
# 2. remind_medicine - 在当前时间顺延2分钟提示吃药
# 这些任务将使用Celery的装饰器来注册到Celery应用中。
from __future__ import absolute_import
from .celery import app
from datetime import datetime, timedelta
import time,json
from tools.myredis import r
from tcourse.models import UserOrder


@app.task
def print_current_time():
    """每分钟打印当前时间的任务"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"当前时间是: {current_time}")
    return f"打印时间: {current_time}"
    
@app.task
def cancel_order(order_id):
    """半小时没支付订单处理，取消"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"当前时间是: {current_time}")
    print(f"取消订单: {order_id}")
    #查询订单号是否在redis list中，如果存在，代码没支付，把订单改为失取消状态，如果不存在 不用处理
    len = r.llen("cancelorder")
    if len>0:
        clist = r.lrange("cancelorder",0,-1)
        clist = json.loads(clist)
        if order_id in clist:
            UserOrder.objects.filter(order_id=order_id).update(status=5)
            r.lrem("cancelorder",order_id)
            
    return f"打印时间: {current_time}"
@app.task
def test_task():
    print("这是一个定时任务")
from tools.sms import sms
@app.task
def send_smscode(phone,message):
    print(f"发送短信验证码到 {phone}")
    sms.send_sms(phone,message)
    return f"短信验证码已发送到 {phone}"


@app.task
def send_email(to_email, subject, content):
    print(f"发送邮件到 {to_email}")
    return f"邮件已发送到 {to_email}"


@app.task
def process_uploaded_lecture_pdf(file_path, course_id):
    """课程文档 OCR 解析与向量化任务"""
    print(f"开始处理课程 PDF 文件: {file_path}, 课程ID: {course_id}")
    # 模拟 PDF 文本抽取耗时
    time.sleep(2)
    print("PDF 文本抽取完成，开始切片处理...")
    # 模拟切片并调用 Embedding 模型
    time.sleep(1)
    chunks = 150
    print(f"文本切片完成，共生成 {chunks} 个片段，开始调用 Embedding 模型...")
    # 模拟调用 Embedding 模型生成向量
    time.sleep(2)
    # 模拟将向量数据持久化到 Elasticsearch
    print("向量数据生成完成，开始持久化到 Elasticsearch...")
    time.sleep(1)
    print(f"课程 {course_id} 的 PDF 向量化任务已完成")
    return {"status": "success", "chunks_created": chunks, "course_id": course_id}


@app.task
def extract_video_subtitles(video_path, course_id):
    """视频字幕提取任务"""
    print(f"开始提取视频字幕: {video_path}, 课程ID: {course_id}")
    # 模拟音视频字幕提取耗时
    time.sleep(3)
    print("字幕提取完成，开始切片存储...")
    # 模拟将字幕文本切片存储
    time.sleep(1)
    subtitle_segments = 45
    print(f"字幕切片完成，共生成 {subtitle_segments} 个字幕片段")
    print(f"课程 {course_id} 的视频字幕提取任务已完成")
    return {"status": "success", "subtitle_segments": subtitle_segments, "course_id": course_id}


@app.task
def generate_learning_report(user_id, course_id):
    """学习数据报表生成任务"""
    print(f"开始生成学习报表, 用户ID: {user_id}, 课程ID: {course_id}")
    # 模拟从数据库获取学习数据
    time.sleep(2)
    print("学习数据获取完成，开始生成学习进度与统计报表...")
    # 模拟生成学习进度与统计报表
    time.sleep(2)
    report_url = f"/reports/{user_id}_{course_id}.pdf"
    print(f"学习报表生成完成，报表地址: {report_url}")
    return {"status": "success", "report_url": report_url, "user_id": user_id, "course_id": course_id}