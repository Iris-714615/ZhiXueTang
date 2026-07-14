"""视频上传与处理模块"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_http_methods
import os
import uuid
from datetime import datetime
import json
import logging

logger = logging.getLogger('apps')

@csrf_exempt
@require_http_methods(["POST"])
def upload_video(request):
    """视频上传接口（支持分片）"""
    try:
        # 1. 获取分片信息
        chunk = request.FILES.get('chunk')
        chunk_index = int(request.POST.get('chunk_index', 0))
        total_chunks = int(request.POST.get('total_chunks', 1))
        filename = request.POST.get('filename', '')
        course_id = request.POST.get('course_id', 'default')
        
        if not chunk:
            return JsonResponse({'code': 400, 'msg': '未找到视频分片'})
        
        # 2. 分片临时存储
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_video_chunks', course_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        chunk_filename = f"{filename}.part.{chunk_index}"
        chunk_path = os.path.join(temp_dir, chunk_filename)
        
        with open(chunk_path, 'wb') as f:
            for chunk_data in chunk.chunks():
                f.write(chunk_data)
        
        logger.info(f"视频分片 {chunk_index+1}/{total_chunks} 上传完成: {chunk_filename}")
        
        # 3. 检查是否所有分片上传完成
        if chunk_index == total_chunks - 1:
            # 合并分片
            final_path = merge_video_chunks(filename, total_chunks, temp_dir, course_id)
            # 触发异步处理
            from tasks.tasks import process_video
            process_video.delay(final_path, filename, course_id)
            
            # 更新课程表中的视频路径
            from .models import Courses
            try:
                course = Courses.objects.get(id=course_id)
                course.video_url = final_path.replace(settings.MEDIA_ROOT, '/upload/')
                course.save()
            except Courses.DoesNotExist:
                logger.warning(f"课程 {course_id} 不存在")
        
        return JsonResponse({'code': 200, 'msg': '分片上传成功', 'chunk_index': chunk_index})
    
    except Exception as e:
        logger.error(f"视频上传失败: {str(e)}")
        return JsonResponse({'code': 500, 'msg': f'上传失败: {str(e)}'})


def merge_video_chunks(filename, total_chunks, temp_dir, course_id):
    """合并视频分片"""
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4()}_{filename}"
    final_dir = os.path.join(settings.MEDIA_ROOT, 'videos', course_id)
    os.makedirs(final_dir, exist_ok=True)
    
    final_path = os.path.join(final_dir, unique_filename)
    
    with open(final_path, 'wb') as final_file:
        for i in range(total_chunks):
            chunk_path = os.path.join(temp_dir, f"{filename}.part.{i}")
            if os.path.exists(chunk_path):
                with open(chunk_path, 'rb') as chunk_file:
                    final_file.write(chunk_file.read())
                os.remove(chunk_path)  # 删除分片
    
    # 删除临时目录
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    logger.info(f"视频分片合并完成: {final_path}")
    return final_path


@require_http_methods(["POST"])
def start_video_processing(request):
    """手动触发视频处理（用于调试或重试）"""
    try:
        data = json.loads(request.body)
        video_path = data.get('video_path')
        course_id = data.get('course_id', 'default')
        
        if not video_path:
            return JsonResponse({'code': 400, 'msg': '缺少视频路径'})
        
        # 触发异步处理
        from tasks.tasks import process_video
        process_video.delay(video_path, os.path.basename(video_path), course_id)
        
        return JsonResponse({'code': 200, 'msg': '视频处理任务已提交'})
    
    except Exception as e:
        logger.error(f"启动视频处理失败: {str(e)}")
        return JsonResponse({'code': 500, 'msg': f'启动失败: {str(e)}'})


@require_http_methods(["GET"])
def get_video_status(request):
    """获取视频处理状态"""
    try:
        video_path = request.GET.get('video_path')
        if not video_path:
            return JsonResponse({'code': 400, 'msg': '缺少视频路径'})
        
        # 检查是否有对应的字幕文件
        srt_path = video_path.replace('.mp4', '.srt')
        subtitle_exists = os.path.exists(srt_path.replace('/upload/', settings.MEDIA_ROOT + '/'))
        
        # 检查是否已构建索引（简单检查是否存在索引标记文件）
        index_path = srt_path.replace('.srt', '_indexed.flag')
        indexed = os.path.exists(index_path)
        
        return JsonResponse({
            'code': 200, 
            'data': {
                'exists': os.path.exists(video_path.replace('/upload/', settings.MEDIA_ROOT + '/')),
                'has_subtitle': subtitle_exists,
                'indexed': indexed
            }
        })
    
    except Exception as e:
        logger.error(f"获取视频状态失败: {str(e)}")
        return JsonResponse({'code': 500, 'msg': f'查询失败: {str(e)}'})