import json
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async


class LiveRoomConsumer(AsyncWebsocketConsumer):
    # 在线人数字典，key 为 room_id，value 为当前在线人数
    # 注意：该字典仅存在于单个进程内存中，生产环境应使用 Redis 等共享存储维护
    _online_counts = {}

    async def connect(self):
        # 从 URL kwargs 获取 room_id
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        # 组名格式：live_room_<room_id>
        self.group_name = f"live_room_{self.room_id}"

        # 加入组
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # 接受 WebSocket 连接
        await self.accept()

        # 在线人数 +1
        self._online_counts[self.room_id] = self._online_counts.get(self.room_id, 0) + 1

        # 广播在线人数更新给房间内所有客户端
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'online_count_message',
                'online_count': self._online_counts[self.room_id],
            }
        )

    async def disconnect(self, close_code):
        # 在线人数 -1，并确保不小于 0
        if self.room_id in self._online_counts:
            self._online_counts[self.room_id] = max(0, self._online_counts[self.room_id] - 1)

        # 离开组
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        # 广播在线人数更新给房间内所有客户端
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'online_count_message',
                'online_count': self._online_counts.get(self.room_id, 0),
            }
        )

    async def receive(self, text_data):
        # 解析 JSON 数据
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            # 非 JSON 数据则忽略
            return

        # 根据消息类型分别处理
        msg_type = data.get('type')

        if msg_type == 'ping':
            # 心跳：收到 ping 直接回 pong
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }))
        elif msg_type == 'danmaku':
            # 弹幕：通过 group_send 广播给房间内所有客户端
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'danmaku_message',
                    'username': data.get('username', '匿名用户'),
                    'content': data.get('content', ''),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                }
            )
        elif msg_type == 'join':
            # 用户加入：广播加入提示消息（复用弹幕通道展示）
            username = data.get('username', '匿名用户')
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'danmaku_message',
                    'username': username,
                    'content': f'{username} 进入直播间',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                }
            )

    async def danmaku_message(self, event):
        # 接收组广播的弹幕消息，发送给前端
        await self.send(text_data=json.dumps({
            'type': 'danmaku',
            'username': event.get('username'),
            'content': event.get('content'),
            'timestamp': event.get('timestamp'),
        }))

    async def online_count_message(self, event):
        # 接收在线人数更新，发送给前端
        await self.send(text_data=json.dumps({
            'type': 'online_count',
            'online_count': event.get('online_count'),
        }))

    async def pong_message(self, event):
        # 心跳响应：接收组广播的 pong 消息并发送给前端
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': event.get('timestamp'),
        }))
