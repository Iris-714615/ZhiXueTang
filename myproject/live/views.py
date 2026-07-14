"""直播间 HTTP 接口。

提供：
- 房间基础信息
- 在线人数查询
- 历史弹幕查询（断线重连补全）
"""

from datetime import datetime

import redis
from django.http import JsonResponse


def _get_redis_client():
    """获取原生 Redis 客户端"""
    return redis.Redis(host='127.0.0.1', port=6379, db=2, decode_responses=True)


# 模拟直播间元数据（生产环境应存数据库）
_ROOM_META = {
    '1': {'title': 'AI 时代的前端工程化实践', 'teacher': '胡椒老师', 'cover': ''},
    '2': {'title': 'Python 数据分析全栈训练营', 'teacher': '清风老师', 'cover': ''},
    '3': {'title': '考研政治冲刺押题直播', 'teacher': '肖老师', 'cover': ''},
}


def room_info(request, room_id):
    """获取直播间信息"""
    meta = _ROOM_META.get(str(room_id), {})
    return JsonResponse({
        'code': 200,
        'data': {
            'room_id': room_id,
            'title': meta.get('title', f'直播间 {room_id}'),
            'teacher': meta.get('teacher', '知学堂讲师'),
            'status': 'live',
        }
    })


def online_count(request, room_id):
    """获取直播间在线人数"""
    try:
        client = _get_redis_client()
        count = int(client.get(f"live:online:{room_id}") or 0)
    except Exception:
        count = 0
    return JsonResponse({
        'code': 200,
        'data': {
            'room_id': room_id,
            'online_count': count,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
    })


def danmaku_history(request, room_id):
    """获取直播间历史弹幕

    Query params:
        limit: 返回条数，默认 50，最大 200
    """
    try:
        limit = min(int(request.GET.get('limit', 50)), 200)
    except ValueError:
        limit = 50

    try:
        client = _get_redis_client()
        stream_key = f"live:danmaku:{room_id}"
        entries = client.xrevrange(stream_key, count=limit)
        entries.reverse()  # 时间正序
        messages = [
            {
                'id': entry_id,
                'username': fields.get('username', '匿名用户'),
                'content': fields.get('content', ''),
                'timestamp': fields.get('timestamp', ''),
            }
            for entry_id, fields in entries
        ]
    except Exception as e:
        messages = []

    return JsonResponse({
        'code': 200,
        'data': {
            'room_id': room_id,
            'messages': messages,
            'total': len(messages),
        }
    })
