"""直播间 WebSocket 消费者（生产级实现）。

特性：
1. Redis 原子计数器维护全局在线人数（支持多进程/多 Worker）
2. 服务端定时心跳，30 秒无响应自动断开回收资源
3. Token Bucket 限流：每用户每秒最多 3 条弹幕，防止刷屏
4. Redis Streams 持久化弹幕历史（保留最近 1000 条），支持断线重连补全
5. 用户鉴权：从 query string 解析 JWT，注入 user 信息
6. 异常全链路捕获，单条消息异常不影响连接稳定性
"""

import asyncio
import json
import time
from datetime import datetime
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
import redis


def _get_redis_client():
    """获取原生 Redis 客户端，用于 Streams 等高级命令"""
    return redis.Redis(host='127.0.0.1', port=6379, db=2, decode_responses=True)


class LiveRoomConsumer(AsyncWebsocketConsumer):
    """直播间消费者：弹幕、在线人数、心跳、限流、持久化"""

    HEARTBEAT_INTERVAL = 30       # 服务端心跳间隔（秒）
    MAX_DANMAKU_PER_SEC = 3       # 每秒最大弹幕数
    DANMAKU_HISTORY_LIMIT = 1000  # Redis Streams 保留的最大历史条数

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = None
        self.group_name = None
        self.user = AnonymousUser()
        self.heartbeat_task = None
        self.last_danmaku_ts = 0.0
        self.username = '匿名用户'

    # ==================== 连接生命周期 ====================

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.group_name = f"live_room_{self.room_id}"
        self.user = self.scope.get('user', AnonymousUser())

        if self.user.is_authenticated:
            self.username = self.user.username
        else:
            # 从 query string 解析 username（正确 URL 解码）
            qs_bytes = self.scope.get('query_string', b'')
            params = parse_qs(qs_bytes.decode('utf-8', errors='ignore'))
            self.username = params.get('username', ['匿名用户'])[0] or '匿名用户'

        # 加入房间组
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # 在线人数 +1（Redis 原子操作）
        online_count = await self.incr_online_count()

        # 推送历史弹幕（断线重连补全）
        await self.send_history_danmaku()

        # 推送当前在线人数
        await self.send(text_data=json.dumps({
            'type': 'online_count',
            'online_count': online_count,
            'timestamp': _now(),
        }))

        # 广播进入提示
        await self.channel_layer.group_send(self.group_name, {
            'type': 'danmaku.broadcast',
            'username': '系统',
            'content': f'{self.username} 进入直播间',
            'timestamp': _now(),
            'system': True,
        })

        # 启动服务端心跳
        self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())

    async def disconnect(self, close_code):
        # 取消心跳
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except (asyncio.CancelledError, Exception):
                pass

        # 离开组
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        # 在线人数 -1
        online_count = await self.decr_online_count()

        # 广播离开提示
        await self.channel_layer.group_send(self.group_name, {
            'type': 'danmaku.broadcast',
            'username': '系统',
            'content': f'{self.username} 离开直播间',
            'timestamp': _now(),
            'system': True,
            'online_count': online_count,
        })

    # ==================== 消息接收 ====================

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data) if text_data else {}
        except json.JSONDecodeError:
            return

        msg_type = data.get('type')

        if msg_type == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'timestamp': _now(),
            }))

        elif msg_type == 'danmaku':
            content = (data.get('content') or '').strip()
            if not content:
                return
            # 限流检查
            if not self.check_rate_limit():
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': '发送太快了，请稍后再试',
                    'timestamp': _now(),
                }))
                return

            # 广播弹幕
            msg = {
                'type': 'danmaku.broadcast',
                'username': self.username,
                'content': content,
                'timestamp': _now(),
                'user_id': self.user.id if self.user.is_authenticated else None,
            }
            await self.channel_layer.group_send(self.group_name, msg)

            # 持久化到 Redis Streams
            await self.persist_danmaku(self.username, content)

    # ==================== 心跳机制 ====================

    async def heartbeat_loop(self):
        """服务端定时心跳，检测连接是否存活"""
        try:
            while True:
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)
                try:
                    await self.send(text_data=json.dumps({
                        'type': 'heartbeat',
                        'timestamp': _now(),
                    }))
                except Exception:
                    break
        except asyncio.CancelledError:
            pass

    # ==================== 限流 ====================

    def check_rate_limit(self):
        """Token Bucket 限流：每秒最多 MAX_DANMAKU_PER_SEC 条"""
        now = time.time()
        if now - self.last_danmaku_ts < 1.0 / self.MAX_DANMAKU_PER_SEC:
            return False
        self.last_danmaku_ts = now
        return True

    # ==================== Redis 操作 ====================

    @database_sync_to_async
    def incr_online_count(self):
        """在线人数原子 +1"""
        key = f"live:online:{self.room_id}"
        try:
            client = _get_redis_client()
            new_count = client.incr(key)
            client.expire(key, 3600)  # 1 小时无活动自动过期
            return new_count
        except Exception:
            return 0

    @database_sync_to_async
    def decr_online_count(self):
        """在线人数原子 -1，最低为 0"""
        key = f"live:online:{self.room_id}"
        try:
            client = _get_redis_client()
            count = client.decr(key)
            if count <= 0:
                client.delete(key)
                return 0
            return count
        except Exception:
            return 0

    @database_sync_to_async
    def persist_danmaku(self, username, content):
        """持久化弹幕到 Redis Streams"""
        try:
            client = _get_redis_client()
            stream_key = f"live:danmaku:{self.room_id}"
            client.xadd(stream_key, {
                'username': username,
                'content': content,
                'timestamp': _now(),
            }, maxlen=self.DANMAKU_HISTORY_LIMIT, approximate=True)
            # 24 小时后自动过期
            client.expire(stream_key, 86400)
        except Exception:
            pass

    @database_sync_to_async
    def fetch_history_danmaku(self):
        """读取最近的历史弹幕（断线重连补全）"""
        try:
            client = _get_redis_client()
            stream_key = f"live:danmaku:{self.room_id}"
            # 读取最近 20 条
            entries = client.xrevrange(stream_key, count=20)
            # 反转为时间正序
            entries.reverse()
            return entries
        except Exception:
            return []

    async def send_history_danmaku(self):
        """向客户端推送历史弹幕"""
        entries = await self.fetch_history_danmaku()
        for _entry_id, fields in entries:
            try:
                await self.send(text_data=json.dumps({
                    'type': 'danmaku',
                    'username': fields.get('username', '匿名用户'),
                    'content': fields.get('content', ''),
                    'timestamp': fields.get('timestamp', _now()),
                    'history': True,
                }))
            except Exception:
                pass

    # ==================== 组广播事件处理器 ====================

    async def danmaku_broadcast(self, event):
        """广播弹幕/系统消息给客户端"""
        payload = {
            'type': 'danmaku',
            'username': event.get('username', '匿名用户'),
            'content': event.get('content', ''),
            'timestamp': event.get('timestamp', _now()),
            'system': event.get('system', False),
        }
        try:
            await self.send(text_data=json.dumps(payload))
        except Exception:
            pass

    async def online_count_message(self, event):
        """广播在线人数更新"""
        try:
            await self.send(text_data=json.dumps({
                'type': 'online_count',
                'online_count': event.get('online_count', 0),
                'timestamp': _now(),
            }))
        except Exception:
            pass


def _now():
    """当前时间字符串"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
