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
def process_video(video_path, original_filename, course_id):
    """异步视频处理任务（转码+字幕提取+向量化）"""
    try:
        import subprocess
        import whisper
        import os
        from django.conf import settings
        
        print(f"开始处理视频: {video_path}, 课程ID: {course_id}")
        
        # 1. 视频转码（降低分辨率/码率）
        output_path = video_path.replace('.mp4', '_optimized.mp4')
        cmd = [
            'ffmpeg', '-i', video_path,
            '-c:v', 'libx264', '-crf', '28',  # 压缩质量
            '-c:a', 'aac', '-b:a', '128k',    # 音频比特率
            '-movflags', '+faststart',         # 流式播放优化
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"视频转码完成: {output_path}")
        
        # 2. 提取音频并转文字（生成字幕）
        audio_path = video_path.replace('.mp4', '.wav')
        cmd = ['ffmpeg', '-i', video_path, '-vn', '-ar', '16000', '-ac', '1', '-f', 'wav', audio_path]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"音频提取完成: {audio_path}")
        
        # 3. 使用 Whisper 生成字幕
        print("开始使用 Whisper 生成字幕...")
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        
        # 4. 保存字幕文件
        srt_path = video_path.replace('.mp4', '.srt')
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments'], 1):
                start = segment['start']
                end = segment['end']
                text = segment['text']
                
                f.write(f"{i}\n")
                f.write(f"{format_time(start)} --> {format_time(end)}\n")
                f.write(f"{text}\n\n")
        
        print(f"字幕文件生成完成: {srt_path}")
        
        # 5. 将字幕内容向量化并存入知识库
        try:
            from ai_service.app.services.rag_service import get_rag_service
            rag_service = get_rag_service()
            
            # 读取字幕内容
            with open(srt_path, 'r', encoding='utf-8') as f:
                subtitle_content = f.read()
            
            # 构建双索引
            build_result = rag_service.build_indexes(course_id, subtitle_content)
            print(f"课程 {course_id} 知识库构建完成: {build_result}")
            
            # 创建索引标记文件
            index_flag_path = srt_path.replace('.srt', '_indexed.flag')
            with open(index_flag_path, 'w') as f:
                f.write(str(datetime.now()))
                
        except ImportError:
            print("警告: 无法导入 ai_service，跳过知识库构建")
        except Exception as e:
            print(f"知识库构建失败: {str(e)}")
        
        # 6. 清理临时音频文件
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        print(f"视频处理任务完成: {output_path}")
        
        return {
            'status': 'success', 
            'video_path': output_path, 
            'subtitle_path': srt_path,
            'course_id': course_id,
            'original_filename': original_filename
        }
        
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 处理失败: {str(e)}")
        return {'status': 'error', 'message': f'FFmpeg 处理失败: {str(e)}'}
    except Exception as e:
        print(f"视频处理失败: {str(e)}")
        return {'status': 'error', 'message': str(e)}


def format_time(seconds):
    """格式化时间戳为 SRT 格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


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