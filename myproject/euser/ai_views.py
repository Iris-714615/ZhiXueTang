"""
AI 网关相关视图：
1. AIAssistantProxyView —— SSE 流式代理，将前端请求转发至 FastAPI AI 微服务
2. CourseProgressView —— 高并发课程学习进度写入接口（先写 Redis 缓存，异步回写 MySQL）

设计参考：开发文档第四/五章"后端混合微服务架构"
"""
import json
import threading
import time

import requests
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response

from tools.myredis import r
from tools.myjwt import myjwt
from euser.models import MyCourse

# FastAPI AI 微服务地址
AI_SERVICE_BASE = "http://localhost:8001"


@method_decorator(csrf_exempt, name='dispatch')
class AIAssistantProxyView(APIView):
    """
    AI 伴学 SSE 代理视图
    将 Django 收到的 /ai/assistant/chat 请求转发至 FastAPI 微服务，
    并以 StreamingHttpResponse 形式把 SSE 流式响应回传前端。
    体现 API 网关统一入口的思想，前端只需访问 Django 8000 端口。
    """

    def post(self, request):
        prompt = request.data.get('prompt')
        course_id = request.data.get('course_id')
        if not prompt or not course_id:
            return Response({"code": 400, "msg": "prompt 和 course_id 不能为空"})

        # 透传前端 Authorization 头，AI 微服务内部校验 JWT
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': auth_header,
        }
        payload = {'prompt': prompt, 'course_id': course_id}

        try:
            upstream = requests.post(
                f"{AI_SERVICE_BASE}/api/v1/ai/assistant/chat",
                json=payload,
                headers=headers,
                stream=True,  # 流式接收，避免阻塞
                timeout=60,
            )
        except requests.exceptions.RequestException as e:
            return Response({"code": 502, "msg": f"AI 服务不可达: {str(e)}"})

        if upstream.status_code != 200:
            return Response({"code": upstream.status_code, "msg": "AI 服务返回错误"})

        def stream_sse():
            """把上游 SSE 字节流按原样透传给前端"""
            try:
                for chunk in upstream.iter_content(chunk_size=512):
                    if chunk:
                        yield chunk
            finally:
                upstream.close()

        resp = StreamingHttpResponse(stream_sse(), content_type='text/event-stream')
        resp['Cache-Control'] = 'no-cache'
        resp['X-Accel-Buffering'] = 'no'
        return resp


@method_decorator(csrf_exempt, name='dispatch')
class CourseProgressView(APIView):
    """
    课程学习进度写入接口（对应文档 4.1 节 Golang 高并发进度记录）
    适配为 Django 实现：
    1. 主线程立即写 Redis 缓存并极速响应
    2. 启动守护线程异步回写 MySQL，避免阻塞请求
    """

    def post(self, request):
        user_id = request.data.get('user_id')
        course_id = request.data.get('course_id')
        progress = request.data.get('progress')
        learned_seconds = request.data.get('learned_seconds', 0)

        if not all([user_id, course_id, progress is not None]):
            return Response({"code": 400, "msg": "参数缺失"})

        # 1. 同步写 Redis 缓存：user:{uid}:progress 哈希表记录各课程进度
        redis_key = f"user:{user_id}:progress"
        r.hset(redis_key, course_id, json.dumps({
            'progress': progress,
            'learned_seconds': learned_seconds,
            'ts': int(time.time())
        }))

        # 2. 异步回写 MySQL（守护线程，主线程不阻塞）
        threading.Thread(
            target=self._save_progress_to_db,
            args=(user_id, course_id, progress, learned_seconds),
            daemon=True
        ).start()

        return Response({"code": 200, "msg": "recorded", "progress": progress})

    def _save_progress_to_db(self, user_id, course_id, progress, learned_seconds):
        """
        异步回写数据库：
        实际生产环境应使用通道(Channel)缓冲 + 连接池批量写入
        这里直接 update MyCourse 记录
        """
        try:
            # 查询用户该课程的 MyCourse 记录
            mc = MyCourse.objects.filter(user_id=user_id, course_id=course_id).first()
            if mc:
                # 进度只增不减
                if progress > mc.progress:
                    mc.progress = progress
                if learned_seconds and learned_seconds > mc.total_time:
                    mc.total_time = learned_seconds
                # 进度达到 100% 时自动置为已完成
                if progress >= 100:
                    mc.status = 3
                mc.save()
        except Exception as e:
            # 实际应记录日志，此处仅打印
            print(f"[CourseProgress] 回写数据库失败: {e}")
